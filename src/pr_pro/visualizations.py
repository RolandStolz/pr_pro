"""Charts for inspecting a program while designing it."""

from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from pr_pro.metrics import session_intensities, session_total_reps
from pr_pro.program import Program

RGB = tuple[float, float, float]
VolumeMetric = Literal['total_reps', 'total_sets']

UNPHASED: str = 'Unphased'


def _phase_of_session(program: Program) -> dict[str, str]:
    """The phase each session belongs to; program_phases holds the reverse."""
    return {
        session_id: phase
        for phase, session_ids in program.program_phases.items()
        for session_id in session_ids
    }


def build_volume_and_intensity_df(
    program: Program, volume_metric: VolumeMetric = 'total_reps'
) -> pd.DataFrame:
    """One row per session: its phase, its volume, and its mean intensity.

    Sessions come in program order, grouped under their phase when the program
    defines phases. Volume counts reps or sets; intensity is the mean over the
    session's sets that have one, as a fraction of 1RM, and NaN when none do.

    Call program.compute_values(...) first: sets carry percentages only once they
    are computed.
    """
    phase_of = _phase_of_session(program)
    rows = []
    for session_id, session in program.workout_session_dict.items():
        intensities = session_intensities(session)
        rows.append(
            {
                'session': session_id,
                'phase': phase_of.get(session_id, UNPHASED),
                'volume': session_total_reps(session)
                if volume_metric == 'total_reps'
                else session.get_number_of_sets(),
                'intensity': sum(intensities) / len(intensities) if intensities else float('nan'),
            }
        )
    return pd.DataFrame(rows, columns=pd.Index(['session', 'phase', 'volume', 'intensity']))


def build_set_intensity_df(program: Program) -> pd.DataFrame:
    """One row per set that carries an intensity, with the session and phase it is in.

    This is the long form the box plots need: a session's spread is its own rows, a
    phase's spread is the rows of all its sessions. Sets without an intensity
    (bodyweight, duration work) have no row at all.
    """
    phase_of = _phase_of_session(program)
    rows = [
        {'session': session_id, 'phase': phase_of.get(session_id, UNPHASED), 'intensity': intensity}
        for session_id, session in program.workout_session_dict.items()
        for intensity in session_intensities(session)
    ]
    return pd.DataFrame(rows, columns=pd.Index(['session', 'phase', 'intensity']))


def _volume_label(volume_metric: VolumeMetric) -> str:
    return 'Total reps' if volume_metric == 'total_reps' else 'Total sets'


def _metric_colors() -> tuple[RGB, RGB]:
    """A colour each for volume and intensity, from whichever palette is active."""
    volume_color, intensity_color = sns.color_palette()[:2]
    return volume_color, intensity_color


def _finish_figure(figure: Figure, intensity_axis: Axes, title: str, show: bool) -> Figure:
    """Shared last touches: read intensity as a percentage, label, show."""
    intensity_axis.set_ylabel('Intensity (% of 1RM)')
    intensity_axis.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    figure.suptitle(title)
    if show:
        plt.show()
    return figure


def plot_session_volume_and_intensity(
    program: Program, volume_metric: VolumeMetric = 'total_reps', show: bool = False
) -> Figure:
    """Volume per session as bars, over the spread of that session's set intensities.

    Call program.compute_values(...) first: sets carry percentages only once they
    are computed.
    """
    sessions = build_volume_and_intensity_df(program, volume_metric)
    sets = build_set_intensity_df(program)
    order = list(sessions['session'])

    figure, (volume_axis, intensity_axis) = plt.subplots(
        2, 1, sharex=True, figsize=(max(7.0, 0.3 * len(order)), 6.0), layout='constrained'
    )

    volume_color, intensity_color = _metric_colors()
    sns.barplot(
        sessions,
        x='session',
        y='volume',
        order=order,
        ax=volume_axis,
        color=volume_color,
    )
    volume_axis.set_ylabel(_volume_label(volume_metric))

    sns.boxplot(
        sets,
        x='session',
        y='intensity',
        order=order,
        ax=intensity_axis,
        color=intensity_color,
    )
    intensity_axis.set_xlabel('Session')
    intensity_axis.tick_params(axis='x', rotation=90, labelsize=8)

    return _finish_figure(figure, intensity_axis, program.name, show)


def plot_phase_volume_and_intensity(
    program: Program, volume_metric: VolumeMetric = 'total_reps', show: bool = False
) -> Figure:
    """Volume and intensity per phase, both as the spread over what the phase contains.

    Volume is the spread of its sessions' volumes, which shows how evenly the work
    sits across the phase; intensity is the spread of all its sets.

    Call program.compute_values(...) first: sets carry percentages only once they
    are computed.
    """
    if not program.program_phases:
        raise ValueError(f'Program {program.name} defines no phases to group by.')

    sessions = build_volume_and_intensity_df(program, volume_metric)
    sets = build_set_intensity_df(program)
    present = set(sessions['phase'])
    order = [phase for phase in (*program.program_phases, UNPHASED) if phase in present]

    figure, (volume_axis, intensity_axis) = plt.subplots(
        2, 1, sharex=True, figsize=(max(7.0, 0.6 * len(order)), 6.0), layout='constrained'
    )

    volume_color, intensity_color = _metric_colors()
    sns.boxplot(
        sessions,
        x='phase',
        y='volume',
        order=order,
        ax=volume_axis,
        color=volume_color,
    )
    volume_axis.set_ylabel(_volume_label(volume_metric))

    sns.boxplot(
        sets,
        x='phase',
        y='intensity',
        order=order,
        ax=intensity_axis,
        color=intensity_color,
    )
    intensity_axis.set_xlabel('Phase')

    return _finish_figure(figure, intensity_axis, program.name, show)


if __name__ == '__main__':  # pragma: no cover
    from pr_pro.configs import ComputeConfig
    from pr_pro.example import get_example_program

    program = get_example_program()
    program.compute_values(ComputeConfig())

    sessions = build_volume_and_intensity_df(program)
    sets = build_set_intensity_df(program)
    assert len(sessions) == len(program.workout_session_dict)
    assert (sessions['volume'] > 0).all(), sessions
    # Every session's mean has to sit inside the spread of its own sets.
    spread = sets.groupby('session')['intensity'].agg(['min', 'max'])
    means = sessions.set_index('session')['intensity']
    assert means.loc[spread.index].between(spread['min'] - 1e-9, spread['max'] + 1e-9).all()

    sns.set_theme()
    plot_session_volume_and_intensity(program, show=True)
