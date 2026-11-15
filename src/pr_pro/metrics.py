from pr_pro.sets import PowerExerciseSet, RepsAndWeightsSet, RepsRPESet, WorkingSet
from pr_pro.workout_session import WorkoutSession


def set_intensity(set: WorkingSet) -> float | None:
    """
    Intensity is a value above 0.
    Usually between 0 and 1, although values above 1 are allowed, since programs may prescribe
    sets above 1RM due to progression.
    """
    # match statement for set types
    match set:
        case RepsRPESet():
            return set.rpe / 10
        case RepsAndWeightsSet():
            return set.percentage
        case PowerExerciseSet():
            return set.percentage
        case _:
            return None


def session_total_reps(session: WorkoutSession) -> int:
    total_reps = 0
    for s in session.get_session_sets():
        if hasattr(s, 'reps') and s.reps is not None:
            total_reps += s.reps
    return total_reps


def session_intensities(session: WorkoutSession) -> list[float]:
    intensities = []
    for s in session.get_session_sets():
        intensity = set_intensity(s)
        if intensity is not None:
            intensities.append(intensity)
    return intensities
