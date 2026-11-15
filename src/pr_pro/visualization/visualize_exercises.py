"""An overview of which exercises are trained when."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from pr_pro.program import Program
from pr_pro.visualization.common import UNPHASED, phase_of_session, phase_order

Amount = Literal['sets', 'reps']


def build_exercise_df(program: Program) -> pd.DataFrame:
    """Long form version of build_exercise_matrix."""
    phase_of = phase_of_session(program)
    rows = [
        {
            'session': session_id,
            'phase': phase_of.get(session_id, UNPHASED),
            'exercise': exercise.name,
            'sets': len(sets),
            'reps': sum(getattr(s, 'reps', 0) or 0 for s in sets),
        }
        for session_id, session in program.workout_session_dict.items()
        for exercise, sets in session.get_exercise_sets().items()
    ]
    return pd.DataFrame(rows, columns=pd.Index(['session', 'phase', 'exercise', 'sets', 'reps']))


def build_exercise_matrix(
    program: Program, group_by: str = 'phase', amount: Amount = 'sets'
) -> pd.DataFrame:
    """The overview as a table: one row per exercise, one column per group."""
    df = build_exercise_df(program)
    if df.empty:
        return pd.DataFrame()

    columns = phase_order(program) if group_by == 'phase' else list(program.workout_session_dict)
    matrix = df.pivot_table(index='exercise', columns=group_by, values=amount, aggfunc='sum')
    matrix = matrix.reindex(columns=[c for c in columns if c in matrix.columns])
    return matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index]


def plot_exercise_overview(
    program: Program,
    group_by: Literal['phase', 'session'] = 'phase',
    amount: Amount = 'sets',
    annotate: bool = True,
    show: bool = False,
) -> Figure:
    """Plot which exercises are trained when, and how much, as a heatmap."""
    matrix = build_exercise_matrix(program, group_by, amount)
    if matrix.empty:
        raise ValueError(f'Program {program.name} trains no exercises to plot.')

    rows, columns = matrix.shape
    figure, axis = plt.subplots(
        figsize=(max(6.0, 0.5 * columns + 3.0), max(4.0, 0.28 * rows + 1.5)),
        layout='constrained',
    )
    sns.heatmap(
        matrix,
        ax=axis,
        cmap='rocket_r',
        annot=annotate,
        fmt='g',
        annot_kws={'size': 7},
        linewidths=0.5,
        cbar_kws={'label': amount.capitalize()},
    )
    axis.set_xlabel(group_by.capitalize())
    axis.set_ylabel('')
    axis.tick_params(axis='y', labelsize=8, rotation=0)
    axis.tick_params(axis='x', labelsize=8, rotation=90 if columns > 12 else 0)
    figure.suptitle(f'{program.name}: {amount} per exercise')

    if show:
        plt.show()
    return figure


if __name__ == '__main__':  # pragma: no cover
    from pr_pro.configs import ComputeConfig
    from pr_pro.example import get_example_program

    program = get_example_program()
    program.compute_values(ComputeConfig())

    sns.set_theme()
    plot_exercise_overview(program, show=True)
