import pytest

from pr_pro.exercises.common import backsquat, deadlift, pullup
from pr_pro.workout_session import (
    exercise_group_from_prev_session,
    single_exercise_from_prev_session,
)


def test_single_exercise_from_prev_session_success(session_a, exercise_component):
    """Tests successfully creating a component from a previous session."""
    session_a.add_component(exercise_component)
    new_component = single_exercise_from_prev_session(session_a, backsquat, sets=+1, weight=-10)
    assert new_component.exercise == backsquat
    assert len(new_component.sets) == 5
    assert new_component.sets[0].weight == 90  # type: ignore


def test_single_exercise_from_prev_session_not_found(session_a):
    """Tests that a ValueError is raised if the exercise is not in the previous session."""
    with pytest.raises(ValueError, match='No previous component found for exercise Backsquat'):
        single_exercise_from_prev_session(session_a, backsquat)


def test_exercise_group_from_prev_session_success(session_a, exercise_group_component):
    """Tests creating an ExerciseGroup from a previous session."""
    session_a.add_component(exercise_group_component)
    print(session_a)
    new_group = exercise_group_from_prev_session(
        session_a, [deadlift, pullup], sets=+1, reps=(+2, +1)
    )
    print(new_group)
    assert {ex.name for ex in new_group.exercises} == {'Deadlift', 'Pullup'}
    assert len(new_group.exercise_sets_dict[deadlift]) == 4
    assert new_group.exercise_sets_dict[deadlift][0].reps == 7  # type: ignore
    assert len(new_group.exercise_sets_dict[pullup]) == 4
    assert new_group.exercise_sets_dict[pullup][0].reps == 9  # type: ignore


def test_exercise_group_from_prev_session_not_found(session_a):
    """Tests ValueError for a non-existent ExerciseGroup."""
    with pytest.raises(
        ValueError, match='No previous component found for exercises Backsquat, Deadlift'
    ):
        exercise_group_from_prev_session(session_a, [backsquat, deadlift])


def test_single_exercise_rel_delta(session_a, exercise_component):
    """Rel scales the previous value instead of adding to it."""
    session_a.add_component(exercise_component)
    from pr_pro.workout_component import Rel

    new_component = single_exercise_from_prev_session(session_a, backsquat, weight=Rel(0.1))
    assert new_component.sets[0].weight == pytest.approx(110)  # type: ignore


def test_single_exercise_rel_mixed_with_additive(session_a, exercise_component):
    """A Rel delta and a plain delta can be combined in one call."""
    session_a.add_component(exercise_component)
    from pr_pro.workout_component import Rel

    new_component = single_exercise_from_prev_session(
        session_a, backsquat, weight=Rel(0.2), reps=-2
    )
    assert new_component.sets[0].weight == pytest.approx(120)  # type: ignore
    assert new_component.sets[0].reps == 3  # type: ignore


def test_exercise_group_rel_delta(session_a, exercise_group_component):
    """Rel works per exercise in a group, alongside None for untouched ones."""
    session_a.add_component(exercise_group_component)
    from pr_pro.workout_component import Rel

    new_group = exercise_group_from_prev_session(
        session_a, [deadlift, pullup], weight=(Rel(0.5), None)
    )
    assert new_group.exercise_sets_dict[deadlift][0].weight == pytest.approx(150)  # type: ignore
