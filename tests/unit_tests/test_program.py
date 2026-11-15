import pytest

from pr_pro.exercises.common import backsquat, bench_press, deadlift, pullup
from pr_pro.workout_component import ExerciseGroup, SingleExercise


def test_add_workout_session_success(basic_program, session_a):
    """Tests successfully adding a workout session."""
    basic_program.add_workout_session(session_a)
    assert basic_program.workout_session_dict['session_a'] == session_a


def test_add_workout_session_duplicate_id_raises_error(basic_program, session_a):
    """Tests that adding a session with a duplicate ID raises a ValueError."""
    basic_program.add_workout_session(session_a)
    with pytest.raises(ValueError, match='Workout session with id session_a already exists'):
        basic_program.add_workout_session(session_a)


def test_add_program_phase_success(basic_program, session_a, session_b):
    """Tests successfully adding a program phase with valid session IDs."""
    basic_program.add_workout_session(session_a).add_workout_session(session_b)
    basic_program.add_program_phase('phase_1', ['session_a', 'session_b'])
    assert basic_program.program_phases['phase_1'] == ['session_a', 'session_b']


def test_add_program_phase_nonexistent_session_id_raises_error(basic_program, session_a):
    """Tests that adding a phase with a non-existent session ID raises a ValueError."""
    basic_program.add_workout_session(session_a)
    with pytest.raises(ValueError, match='One or more session IDs do not exist'):
        basic_program.add_program_phase('phase_1', ['session_a', 'non_existent_session'])


def test_get_workout_session_by_id(basic_program, session_a):
    """Tests retrieving an existing and non-existing workout session."""
    basic_program.add_workout_session(session_a)
    assert basic_program.get_workout_session_by_id('session_a') == session_a
    assert basic_program.get_workout_session_by_id('session_z') is None


def test_add_and_update_best_exercise_value(basic_program):
    """Tests adding and then updating a best exercise value."""
    basic_program.add_best_exercise_value(bench_press, 100.0)
    assert basic_program.best_exercise_values[bench_press] == 100.0
    basic_program.add_best_exercise_value(bench_press, 105.5)
    assert basic_program.best_exercise_values[bench_press] == 105.5


def test_json_round_trip_keeps_set_types(tmp_path):
    """Set classes must survive serialization. PowerExerciseSet used to come back as a
    RepsAndWeightsSet, since both accept reps/weight/percentage."""
    from pr_pro.exercise import PowerExercise
    from pr_pro.program import Program
    from pr_pro.sets import PowerExerciseSet
    from pr_pro.workout_component import SingleExercise
    from pr_pro.workout_session import WorkoutSession

    snatch = PowerExercise(name='Snatch')
    program = Program(name='Power program').add_workout_session(
        WorkoutSession(id='W1D1').add_component(
            SingleExercise(exercise=snatch).add_repeating_set(2, snatch.create_set(2, weight=50))
        )
    )
    path = tmp_path.joinpath('program.json')
    program.write_json_file(path)
    loaded = Program.from_json_file(path)

    component = loaded.workout_session_dict['W1D1'].workout_components[0]
    assert isinstance(component.sets[0], PowerExerciseSet)
    assert loaded == program


def test_get_exercise_names_in_order_of_introduction(example_program):
    names = example_program.get_exercise_names()

    assert names == list(dict.fromkeys(names))
    assert 'Backsquat' in names


def test_filter_exercises_keeps_only_the_named_ones(example_program):
    filtered = example_program.filter_exercises(['Backsquat'])

    assert filtered.get_exercise_names() == ['Backsquat']
    # Sessions and phases survive, so the program keeps its shape.
    assert list(filtered.workout_session_dict) == list(example_program.workout_session_dict)
    assert filtered.program_phases == example_program.program_phases


def test_filter_exercises_leaves_the_original_alone(example_program):
    before = example_program.get_exercise_names()
    example_program.filter_exercises(['Backsquat'])

    assert example_program.get_exercise_names() == before


def test_filter_exercises_trims_groups_to_the_named_members(session_a, basic_program):
    basic_program.add_workout_session(
        session_a.add_component(
            ExerciseGroup(exercises=[deadlift, pullup]).add_repeating_group_sets(
                2, {deadlift: deadlift.create_set(5, weight=100), pullup: pullup.create_set(8)}
            )
        )
    )

    filtered = basic_program.filter_exercises(['Deadlift'])
    group = filtered.workout_session_dict[session_a.id].workout_components[0]

    assert [exercise.name for exercise in group.exercises] == ['Deadlift']


def test_filter_exercises_drops_a_group_with_no_named_member(session_a, basic_program):
    basic_program.add_workout_session(
        session_a.add_component(
            ExerciseGroup(exercises=[deadlift, pullup]).add_repeating_group_sets(
                2, {deadlift: deadlift.create_set(5, weight=100), pullup: pullup.create_set(8)}
            )
        ).add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                3, backsquat.create_set(5, weight=100)
            )
        )
    )

    filtered = basic_program.filter_exercises(['Backsquat'])
    components = filtered.workout_session_dict[session_a.id].workout_components

    assert [c.exercise.name for c in components] == ['Backsquat']


def test_filter_exercises_rejects_an_unknown_exercise(example_program):
    with pytest.raises(ValueError, match='no exercise'):
        example_program.filter_exercises(['Zercher carry'])
