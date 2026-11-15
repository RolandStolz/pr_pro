import matplotlib.pyplot as plt
import pandas as pd
import pytest

from pr_pro.exercises.common import backsquat, deadlift
from pr_pro.program import Program
from pr_pro.visualization.visualize_exercises import (
    build_exercise_df,
    build_exercise_matrix,
    plot_exercise_overview,
)
from pr_pro.workout_component import SingleExercise
from pr_pro.workout_session import WorkoutSession


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close('all')


def test_df_has_a_row_per_exercise_in_a_session(example_program):
    df = build_exercise_df(example_program)

    assert list(df.columns) == ['session', 'phase', 'exercise', 'sets', 'reps']
    first = example_program.workout_session_dict['W1D1']
    assert len(df[df['session'] == 'W1D1']) == len(first.get_exercise_sets())
    assert (df['sets'] > 0).all()


def test_matrix_columns_follow_the_program_phases(example_program):
    matrix = build_exercise_matrix(example_program)

    assert list(matrix.columns) == list(example_program.program_phases)


def test_matrix_is_blank_where_an_exercise_is_untrained():
    """A phase that never trains an exercise leaves that cell empty, not zero."""
    program = (
        Program(name='Two phases')
        .add_workout_session(
            WorkoutSession(id='A').add_component(
                SingleExercise(exercise=backsquat).add_repeating_set(
                    3, backsquat.create_set(5, weight=100)
                )
            )
        )
        .add_workout_session(
            WorkoutSession(id='B').add_component(
                SingleExercise(exercise=deadlift).add_repeating_set(
                    2, deadlift.create_set(5, weight=100)
                )
            )
        )
    )
    program.add_program_phase('P1', ['A']).add_program_phase('P2', ['B'])

    matrix = build_exercise_matrix(program)

    assert matrix.loc[backsquat.name, 'P1'] == 3
    assert pd.isna(matrix.loc[backsquat.name, 'P2'])
    assert pd.isna(matrix.loc[deadlift.name, 'P1'])


def test_matrix_puts_the_most_trained_exercise_first(example_program):
    totals = build_exercise_matrix(example_program).sum(axis=1)

    assert totals.is_monotonic_decreasing


def test_matrix_sums_sets_over_the_sessions_of_a_phase(example_program):
    by_phase = build_exercise_matrix(example_program, 'phase')
    by_session = build_exercise_matrix(example_program, 'session')

    phase, sessions = next(iter(example_program.program_phases.items()))
    assert by_phase.loc[backsquat.name, phase] == by_session.loc[backsquat.name, sessions].sum()


def test_plot_draws_a_cell_per_exercise_and_group(example_program):
    (axis, _colorbar) = plot_exercise_overview(example_program).axes
    matrix = build_exercise_matrix(example_program)

    assert [label.get_text() for label in axis.get_yticklabels()] == list(matrix.index)
    assert [label.get_text() for label in axis.get_xticklabels()] == list(matrix.columns)


def test_plot_needs_exercises():
    with pytest.raises(ValueError, match='no exercises'):
        plot_exercise_overview(Program(name='Empty program'))


def test_an_exercise_in_two_components_pools_its_sets(session_a, exercise_component):
    session_a.add_component(exercise_component).add_single_exercise(backsquat)

    assert set(session_a.get_exercise_sets()) == {backsquat}
    assert len(session_a.get_exercise_sets()[backsquat]) == len(exercise_component.sets)
