"""Charts for inspecting a program while designing it."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from pr_pro.metrics import INTENSITY, TOTAL_REPS, Metric
from pr_pro.program import Program
from pr_pro.visualization.common import UNPHASED, phase_of_session, phase_order

DEFAULT_VOLUME_INTENSITY_METRICS = (TOTAL_REPS, INTENSITY)


def build_metrics_df(program: Program, metrics: Sequence[Metric]) -> pd.DataFrame:
    """Long form: one row per value a metric takes, with the session and phase it is in.

    A session contributes one row for its total reps and one for each of its sets'
    intensities, so grouping by session gives a session's own spread while grouping
    by phase pools the spread of its sessions. Sessions come in program order.

    Call program.compute_values(...) first: sets carry percentages only once they
    are computed.
    """
    phase_of = phase_of_session(program)
    rows = [
        {
            'session': session_id,
            'phase': phase_of.get(session_id, UNPHASED),
            'metric': metric.label,
            'value': value,
        }
        for session_id, session in program.workout_session_dict.items()
        for metric in metrics
        for value in metric.values(session)
    ]
    return pd.DataFrame(rows, columns=pd.Index(['session', 'phase', 'metric', 'value']))


def _plot_metrics(
    program: Program, metrics: Sequence[Metric], group_by: str, order: list[str], show: bool
) -> Figure:
    """One axes per metric, over a shared x axis of groups."""
    df = build_metrics_df(program, metrics)

    figure, axes_array = plt.subplots(
        len(metrics),
        1,
        sharex=True,
        squeeze=False,
        figsize=(max(7.0, 0.3 * len(order)), 3.0 * len(metrics)),
        layout='constrained',
    )
    axes: list[Axes] = list(axes_array.flat)
    # A metric that produced no values at all has no group here, and no panel drawn.
    by_metric = {str(label): frame for label, frame in df.groupby('metric')}

    for axis, metric, color in zip(axes, metrics, sns.color_palette()):
        axis.set_ylabel(metric.label)
        data = by_metric.get(metric.label)
        if data is None:
            continue
        # One value per group leaves no spread to show, so it stays a bar.
        if data.groupby(group_by).size().max() == 1:
            sns.barplot(data, x=group_by, y='value', order=order, ax=axis, color=color)
        else:
            sns.boxplot(data, x=group_by, y='value', order=order, ax=axis, color=color)

    axes[-1].set_xlabel(group_by.capitalize())
    if len(order) > 12:
        axes[-1].tick_params(axis='x', rotation=90, labelsize=8)
    figure.suptitle(program.name)

    if show:
        plt.show()
    return figure


def plot_session_metrics(
    program: Program,
    metrics: Sequence[Metric] = DEFAULT_VOLUME_INTENSITY_METRICS,
    show: bool = False,
) -> Figure:
    """Plot each metric per session."""
    return _plot_metrics(program, metrics, 'session', list(program.workout_session_dict), show)


def plot_phase_metrics(
    program: Program,
    metrics: Sequence[Metric] = DEFAULT_VOLUME_INTENSITY_METRICS,
    show: bool = False,
) -> Figure:
    """Plot each metric per phase, pooling the values of the sessions it holds."""
    if not program.program_phases:
        raise ValueError(f'Program {program.name} defines no phases to group by.')

    return _plot_metrics(program, metrics, 'phase', phase_order(program), show)


if __name__ == '__main__':  # pragma: no cover
    from pr_pro.configs import ComputeConfig
    from pr_pro.example import get_example_program

    program = get_example_program()
    program.compute_values(ComputeConfig())

    sns.set_theme()
    plot_phase_metrics(program, show=True)
