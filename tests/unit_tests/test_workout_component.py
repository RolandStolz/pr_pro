import pytest
from pr_pro.sets import RepsAndWeightsSet, RepsRPESet
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.exercises.common import backsquat, deadlift, pullup, bench_press


class TestSingleExercise:
    """Tests for the SingleExercise component."""

    def test_creation_and_sets(self):
        """Tests basic creation and adding sets."""
        component = SingleExercise(exercise=backsquat)
        component.add_set(backsquat.create_set(reps=5, weight=100))
        component.add_repeating_set(2, backsquat.create_set(reps=8, weight=80))

        assert len(component.sets) == 3
        assert component.sets[0].weight == 100  # type: ignore
        assert component.sets[1].weight == 80  # type: ignore
        assert component.sets[2].reps == 8  # type: ignore

    def test_type_validation_failure(self):
        """Tests that adding a set of the wrong type raises a ValueError."""
        # A generic WorkingSet is not the same as a RepsAndWeightSet
        wrong_set = RepsRPESet(reps=1, rpe=5)
        with pytest.raises(
            ValueError,
            match='1 validation error for SingleExercise\n  Value error, All sets must be of type RepsAndWeightsSet',
        ):
            SingleExercise(exercise=backsquat, sets=[wrong_set])

    def test_from_prev_component(self):
        """Tests the powerful from_prev_component method."""
        prev_component = SingleExercise(exercise=backsquat)
        prev_component.add_repeating_set(3, backsquat.create_set(reps=10, weight=100))

        # Test case 1: Add 1 set, decrease reps by 2, increase weight by 10
        new_comp = SingleExercise.from_prev_component(prev_component, sets=+1, reps=-2, weight=+10)
        assert type(new_comp.sets) is list
        assert isinstance(new_comp.sets[0], RepsAndWeightsSet)

        assert len(new_comp.sets) == 4  # 3 + 1
        assert new_comp.sets[0].reps == 8  # 10 - 2
        assert new_comp.sets[0].weight == 110  # 100 + 10

        # Ensure original component is unchanged
        assert isinstance(prev_component.sets[0], RepsAndWeightsSet)
        assert len(prev_component.sets) == 3
        assert prev_component.sets[0].reps == 10


class TestExerciseGroup:
    """Tests for the ExerciseGroup component."""

    def test_creation_and_add_remove_exercise(self):
        """Tests group creation, adding, and removing exercises."""
        group = ExerciseGroup(exercises=[bench_press, pullup])
        assert list(group.exercise_sets_dict.keys()) == [bench_press, pullup]

        with pytest.raises(ValueError, match='Exercise Pullup is already part of this group.'):
            group.add_exercise(pullup)

        # Test adding a duplicate exercise
        with pytest.raises(ValueError, match='must be unique in the group'):
            ExerciseGroup(exercises=[bench_press, bench_press])

        # Test removing an exercise
        with pytest.raises(ValueError, match='Exercise Backsquat is not part of this group.'):
            group.remove_exercise(backsquat)

        group.remove_exercise(pullup)
        assert group.exercises == [bench_press]
        assert pullup not in group.exercise_sets_dict

        # Test adding another exercise
        group.add_exercise(backsquat)
        group.add_repeating_set(2, backsquat.create_set(1, 100), exercise=backsquat)

    def test_add_group_sets(self):
        """Tests adding sets to the entire group at once."""
        group = ExerciseGroup(exercises=[bench_press, deadlift])
        group.add_repeating_group_sets(
            3,
            {
                bench_press: bench_press.create_set(5, 100),
                deadlift: deadlift.create_set(8, 70),
            },
        )

        assert isinstance(group.exercise_sets_dict[bench_press][0], RepsAndWeightsSet)
        assert isinstance(group.exercise_sets_dict[deadlift][0], RepsAndWeightsSet)

        assert len(group.exercise_sets_dict[bench_press]) == 3
        assert len(group.exercise_sets_dict[deadlift]) == 3
        assert group.exercise_sets_dict[bench_press][0].weight == 100  # type: ignore
        assert group.exercise_sets_dict[deadlift][2].reps == 8  # type: ignore

    def test_from_prev_component_group(self):
        """Tests the from_prev_component method for groups."""
        prev_group = ExerciseGroup(exercises=[bench_press, deadlift])
        prev_group.add_repeating_group_sets(
            2,
            {
                bench_press: bench_press.create_set(reps=10, weight=60),
                deadlift: deadlift.create_set(reps=12, weight=50),
            },
        )

        # Increase reps by 2 for bench, 0 for row. Increase weight by 5kg for both.
        new_group = ExerciseGroup.from_prev_component(prev_group, reps=(+2, 0), weight=(+5, +5))

        assert len(new_group.exercise_sets_dict[bench_press]) == 2

        assert isinstance(new_group.exercise_sets_dict[bench_press][0], RepsAndWeightsSet)
        assert isinstance(new_group.exercise_sets_dict[deadlift][0], RepsAndWeightsSet)

        # Check bench press sets (reps +2, weight +5)
        assert new_group.exercise_sets_dict[bench_press][0].reps == 12  # type: ignore
        assert new_group.exercise_sets_dict[bench_press][0].weight == 65  # type: ignore

        # Check row sets (reps +0, weight +5)
        assert new_group.exercise_sets_dict[deadlift][0].reps == 12  # type: ignore
        assert new_group.exercise_sets_dict[deadlift][0].weight == 55  # type: ignore

        # Check original is unchanged
        assert prev_group.exercise_sets_dict[bench_press][0].reps == 10  # type: ignore
