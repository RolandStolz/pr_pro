"""A table of what a handful of sessions actually contain, for reading side by side."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import groupby

import pandas as pd

from pr_pro.program import Program
from pr_pro.sets import DurationSet, WorkingSet_t, format_duration


def _reps_text(working_set: WorkingSet_t) -> str:
    """What the set asks for, before any load: its reps, or its duration."""
    if isinstance(working_set, DurationSet):
        return format_duration(working_set.duration)
    return str(working_set.reps)


def sets_text(sets: Sequence[WorkingSet_t]) -> str:
    """A session's sets for one exercise, as the rep schemes it asks for.

    Consecutive sets wanting the same reps become one entry, 4x5, whatever they are
    loaded with. The loads are in print(session), the PDF and the metric plots; here
    they would make a column as wide as its heaviest cell for no gain in overview.
    """
    entries = []
    for reps_text, run in groupby(_reps_text(s) for s in sets):
        count = len(list(run))
        entries.append(f'{count}x{reps_text}' if count > 1 else reps_text)
    return ', '.join(entries)


def build_session_table(
    program: Program,
    session_ids: Sequence[str] | None = None,
    exercises: Sequence[str] | None = None,
) -> pd.DataFrame:
    """
    A table of what a handful of sessions actually contain, for reading side by side.
    """
    if session_ids is None:
        session_ids = list(program.workout_session_dict)
    unknown_sessions = [sid for sid in session_ids if sid not in program.workout_session_dict]
    if unknown_sessions:
        raise ValueError(f'Program {program.name} has no session {unknown_sessions}.')

    columns = {
        session_id: {
            exercise.name: sets_text(sets)
            for exercise, sets in program.workout_session_dict[session_id]
            .get_exercise_sets()
            .items()
        }
        for session_id in session_ids
    }
    # dict keeps insertion order, so the exercises stay in the order they appear.
    rows = list(dict.fromkeys(name for column in columns.values() for name in column))
    table = pd.DataFrame(columns, index=pd.Index(rows, name='exercise')).fillna('')

    if exercises is None:
        return table

    known = program.get_exercise_names()
    unknown = [name for name in exercises if name not in known]
    if unknown:
        raise ValueError(f'Program {program.name} trains no exercise {unknown}.')
    return table.reindex(index=pd.Index(exercises, name='exercise'), fill_value='')


def print_session_table(
    program: Program,
    session_ids: Sequence[str] | None = None,
    exercises: Sequence[str] | None = None,
    transpose: bool = True,
) -> None:
    """
    Prints a concise overview of the exercises used for sessions.
    You can focus on specific exercises by providing a list as exercises.
    If the result does not look nice due to text wrapping, try changing transpose.
    """
    table = build_session_table(program, session_ids, exercises)
    print((table.T if transpose else table).to_string())


if __name__ == '__main__':  # pragma: no cover
    from pr_pro.configs import ComputeConfig
    from pr_pro.example import get_example_program

    program = get_example_program()
    program.compute_values(ComputeConfig())

    print_session_table(program, transpose=False)
