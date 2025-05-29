_EXERCISE_REGISTRY_BY_KEY_STRING = {}

# Note: cannot use Exercise type hint here due to circular import


def register_exercise(exercise) -> None:
    """
    Register an exercise in the registry.
    This is only necessary when you intent to load a program from a file.
    """
    key = exercise.__str__()
    if key in _EXERCISE_REGISTRY_BY_KEY_STRING:
        raise ValueError(f"Exercise with name '{exercise.name}' is already registered.")
    _EXERCISE_REGISTRY_BY_KEY_STRING[key] = exercise


def get_exercise_by_key_string(key: str):
    """Retrieve an exercise from the registry by its string key."""
    if key not in _EXERCISE_REGISTRY_BY_KEY_STRING:
        raise KeyError(f"Exercise with key '{key}' not found in the registry.")
    return _EXERCISE_REGISTRY_BY_KEY_STRING[key]
