import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import PathPatch, Rectangle

from pr_pro.metrics import INTENSITY, TOTAL_REPS
from pr_pro.program import Program
from pr_pro.visualizations import (
    UNPHASED,
    build_metrics_df,
    plot_phase_metrics,
    plot_session_metrics,
)
from pr_pro.workout_session import WorkoutSession


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close('all')


def test_df_has_a_row_per_session_and_per_set(example_program):
    df = build_metrics_df(example_program, [TOTAL_REPS, INTENSITY])

    assert list(df.columns) == ['session', 'phase', 'metric', 'value']
    counts = df.groupby('metric').size()
    assert counts[TOTAL_REPS.label] == len(example_program.workout_session_dict)
    assert counts[INTENSITY.label] > counts[TOTAL_REPS.label]


def test_df_labels_sessions_outside_a_phase(example_program):
    example_program.add_workout_session(WorkoutSession(id='extra'))

    phases = build_metrics_df(example_program, [TOTAL_REPS]).set_index('session')['phase']
    assert phases['extra'] == UNPHASED
    assert phases['W1D1'] == 'W1'


def test_session_plot_draws_a_bar_per_session(example_program):
    (axis,) = plot_session_metrics(example_program, [TOTAL_REPS]).axes

    assert len(axis.patches) == len(example_program.workout_session_dict)
    assert all(isinstance(patch, Rectangle) for patch in axis.patches)


def test_phase_plot_pools_sessions_into_a_box_per_phase(example_program):
    (axis,) = plot_phase_metrics(example_program, [TOTAL_REPS]).axes

    assert len(axis.patches) == len(example_program.program_phases)
    assert all(isinstance(patch, PathPatch) for patch in axis.patches)


def test_one_axes_per_metric(example_program):
    figure = plot_session_metrics(example_program, [TOTAL_REPS, INTENSITY])

    assert [axis.get_ylabel() for axis in figure.axes] == [TOTAL_REPS.label, INTENSITY.label]


def test_phase_plot_needs_phases():
    with pytest.raises(ValueError, match='no phases'):
        plot_phase_metrics(Program(name='Unphased program'))
