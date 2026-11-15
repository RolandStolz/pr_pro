"""A table of what a handful of sessions actually contain, for reading side by side."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import groupby

import pandas as pd

from pr_pro.metrics import set_intensity
from pr_pro.program import Program
from pr_pro.sets import DurationSet, WorkingSet_t, format_duration


def _reps_text(working_set: WorkingSet_t) -> str:
    """What the set asks for, before any load: its reps, or its duration."""
    if isinstance(working_set, DurationSet):
        return format_duration(working_set.duration)
    reps = getattr(working_set, 'reps', None)
    return str(reps) if reps is not None else str(working_set)


def _load(working_set: WorkingSet_t) -> tuple[float, str] | None:
    """How heavy the set is, as a value and its unit: kilos if known, else % of 1RM."""
    weight = getattr(working_set, 'weight', None)
    if weight is not None:
        # One decimal, as the PDF tables use for the same numbers.
        return round(weight, 1), 'kg'
    intensity = set_intensity(working_set)
    return (round(intensity * 100), '%') if intensity is not None else None


def sets_text(sets: Sequence[WorkingSet_t]) -> str:
    """A session's sets for one exercise, in as few entries as say it.
    Consecutive sets asking the same reps become one entry, 4x5, and their loads
    collapse to the span they cover, so a ramp reads 6x1 @ 60-85kg rather than six
    entries. A change of reps starts a new entry, since that is the structure worth
    seeing here; the individual sets are in print(session) and the PDF.
    """
    entries = []
    for (reps_text, unit), run in groupby(sets, key=lambda s: (_reps_text(s), _unit(s))):
        group = list(run)
        count = f'{len(group)}x' if len(group) > 1 else ''
        loads = [load[0] for s in group if (load := _load(s)) is not None]
        if not loads:
            entries.append(f'{count}{reps_text}')
        elif min(loads) == max(loads):
            entries.append(f'{count}{reps_text} @ {loads[0]:g}{unit}')
        else:
            entries.append(f'{count}{reps_text} @ {min(loads):g}-{max(loads):g}{unit}')
    return ', '.join(entries)


def _unit(working_set: WorkingSet_t) -> str:
    """Kilos and percentages never share an entry, so the unit is part of the key."""
    load = _load(working_set)
    return load[1] if load else ''


def build_session_table(
    program: Program,
    session_ids: Sequence[str] | None = None,
    exercises: Sequence[str] | None = None,
) -> pd.DataFrame:
    """
    A table of what a handful of sessions actually contain, for reading side by side.
    Call program.compute_values(...) first for the loads to show.
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

    unknown = [name for name in exercises if name not in program.get_exercise_names()]
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
