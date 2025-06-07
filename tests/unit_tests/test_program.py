import pytest
from pr_pro.exercises.common import bench_press


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
