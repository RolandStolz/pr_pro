import pytest

from pr_pro.example import get_example_program, get_simple_example_program
from pr_pro.program import Program
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession
from pr_pro.exercises.common import deadlift, pullup, backsquat


@pytest.fixture
def simple_example_program():
    return get_simple_example_program()


@pytest.fixture
def example_program():
    return get_example_program()


@pytest.fixture
def session_a():
    """Fixture for a real WorkoutSession 'A'."""
    return WorkoutSession(id='session_a', notes='Push Day')


@pytest.fixture
def session_b():
    """Fixture for a real WorkoutSession 'B'."""
    return WorkoutSession(id='session_b', notes='Pull Day')


@pytest.fixture
def basic_program():
    """Fixture for a basic Program instance."""
    return Program(name='Strength Program')


@pytest.fixture
def exercise_component():
    return SingleExercise(exercise=backsquat).add_repeating_set(
        4, backsquat.create_set(5, weight=100)
    )


@pytest.fixture
def exercise_group_component():
    return ExerciseGroup(exercises=[deadlift, pullup]).add_repeating_group_sets(
        3,
        {
            deadlift: deadlift.create_set(5, weight=100),
            pullup: pullup.create_set(8),
        },
    )
