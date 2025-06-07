from pr_pro.exercises.common import backsquat, deadlift, pullup


def test_add_component(session_a, exercise_component):
    """Tests adding a component and method chaining."""
    session_a.add_component(exercise_component).add_component(exercise_component)
    assert len(session_a.workout_components) == 2


def test_add_aliases(session_a, exercise_component):
    """Tests the add_co and add_se aliases."""
    session_a.add_co(exercise_component)
    assert len(session_a.workout_components) == 1
    session_a.add_se(backsquat)
    assert len(session_a.workout_components) == 2
    assert session_a.workout_components[1].exercise.name == 'Backsquat'


def test_get_component_by_exercise(session_a, exercise_component):
    """Tests finding a SingleExercise component."""
    session_a.add_component(exercise_component)
    found = session_a.get_component_by_exercise(backsquat)
    assert found == exercise_component
    not_found = session_a.get_component_by_exercise(deadlift)
    assert not_found is None


def test_get_component_by_exercise_group(session_a, exercise_group_component):
    """Tests finding an ExerciseGroup component."""
    session_a.add_component(exercise_group_component)
    found = session_a.get_component_by_exercise_group([deadlift, pullup])
    assert found == exercise_group_component
    not_found = session_a.get_component_by_exercise_group([backsquat])
    assert not_found is None


def test_get_number_of_exercises(session_a, exercise_component, exercise_group_component):
    """Tests the calculation of the total number of exercises."""
    assert session_a.get_number_of_exercises() == 0
    session_a.add_component(exercise_component)
    assert session_a.get_number_of_exercises() == 1
    session_a.add_component(exercise_group_component)
    assert session_a.get_number_of_exercises() == 3


def test_get_number_of_sets(session_a, exercise_component, exercise_group_component):
    """Tests the calculation of the total number of sets."""
    assert session_a.get_number_of_sets() == 0
    session_a.add_component(exercise_component)
    assert session_a.get_number_of_sets() == 4
    session_a.add_component(exercise_group_component)
    assert session_a.get_number_of_sets() == 10  # 4 + 2*3
