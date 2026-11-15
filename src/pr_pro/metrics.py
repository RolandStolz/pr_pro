from collections.abc import Callable
from typing import NamedTuple

from pr_pro.sets import PowerExerciseSet, RepsAndWeightsSet, RepsRPESet, WorkingSet
from pr_pro.workout_session import WorkoutSession


class Metric(NamedTuple):
    label: str
    values: Callable[[WorkoutSession], list[float]]


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


def set_relative_intensity(set: WorkingSet) -> float | None:
    match set:
        case RepsAndWeightsSet():
            return set.relative_percentage
        case _:
            return None


def session_total_reps(session: WorkoutSession) -> int:
    total_reps = 0
    for s in session.get_session_sets():
        if hasattr(s, 'reps') and s.reps is not None:  # pyright: ignore[reportAttributeAccessIssue]
            total_reps += s.reps  # pyright: ignore[reportAttributeAccessIssue]
    return total_reps


def session_intensities(session: WorkoutSession) -> list[float]:
    intensities = []
    for s in session.get_session_sets():
        intensity = set_intensity(s)
        if intensity is not None:
            intensities.append(intensity)
    return intensities


def session_relative_intensities(session: WorkoutSession) -> list[float]:
    relative_intensities = []
    for s in session.get_session_sets():
        relative_intensity = set_relative_intensity(s)
        if relative_intensity is not None:
            relative_intensities.append(relative_intensity)
    return relative_intensities


TOTAL_REPS = Metric('Total reps', lambda session: [float(session_total_reps(session))])
TOTAL_SETS = Metric('Total sets', lambda session: [float(session.get_number_of_sets())])
INTENSITY = Metric('Intensity (fraction of 1RM)', session_intensities)
RELATIVE_INTENSITY = Metric(
    'Relative intensity (set estimated 1RM fraction of 1RM)', session_relative_intensities
)
