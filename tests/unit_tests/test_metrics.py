import pytest

from pr_pro.configs import ComputeConfig
from pr_pro.exercise import (
    PowerExercise,
    RepsAndWeightsExercise,
    RepsExercise,
    RepsRPEExercise,
)
from pr_pro.metrics import (
    INTENSITY,
    RELATIVE_INTENSITY,
    TOTAL_REPS,
    TOTAL_SETS,
    session_intensities,
    session_total_reps,
    set_intensity,
)
from pr_pro.workout_component import SingleExercise
from pr_pro.workout_session import WorkoutSession

squat = RepsAndWeightsExercise(name='Squat')
clean = PowerExercise(name='Clean')
row = RepsRPEExercise(name='Row')
pullup = RepsExercise(name='Pullup')


@pytest.fixture
def mixed_session():
    """Two sets carrying an intensity, three without."""
    session = (
        WorkoutSession(id='S')
        .add_component(
            SingleExercise(exercise=squat).add_repeating_set(2, squat.create_set(5, percentage=0.7))
        )
        .add_component(SingleExercise(exercise=pullup).add_repeating_set(3, pullup.create_set(10)))
    )
    session.compute_values({squat: 100}, ComputeConfig())
    return session


def test_set_intensity_by_set_type():
    assert set_intensity(squat.create_set(5, percentage=0.7)) == 0.7
    assert set_intensity(clean.create_set(2, percentage=0.8)) == 0.8
    assert set_intensity(row.create_set(8, rpe=7)) == 0.7
    # A set with no notion of load has no intensity.
    assert set_intensity(pullup.create_set(10)) is None


def test_session_total_reps_counts_every_set(mixed_session):
    assert session_total_reps(mixed_session) == 2 * 5 + 3 * 10


def test_session_intensities_skips_sets_without_one(mixed_session):
    assert session_intensities(mixed_session) == [0.7, 0.7]


def test_metrics_return_one_value_per_session_or_per_set(mixed_session):
    assert TOTAL_REPS.values(mixed_session) == [40.0]
    assert TOTAL_SETS.values(mixed_session) == [5.0]
    assert INTENSITY.values(mixed_session) == [0.7, 0.7]
    assert RELATIVE_INTENSITY.values(mixed_session) == [0.7875, 0.7875]
