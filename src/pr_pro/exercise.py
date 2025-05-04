from abc import abstractmethod
from datetime import time
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict

from pr_pro.sets import (
    DurationSet,
    OlyWeightLiftingSet,
    RepsAndWeightsSet,
    RepsRPESet,
    RepsSet,
    WorkingSet,
)


class Exercise(BaseModel):
    set_class: ClassVar[type[WorkingSet]] = WorkingSet
    name: str
    model_config = ConfigDict(frozen=True)

    @abstractmethod
    @staticmethod
    def create_set(reps: int) -> WorkingSet: ...

    if TYPE_CHECKING:
        # For pylance
        def __hash__(self) -> int: ...


class RepsExercise(Exercise):
    set_class = RepsSet

    @staticmethod
    def create_set(reps: int) -> RepsSet:
        return RepsSet(reps=reps)

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...


class RepsRPEExercise(RepsExercise):
    set_class = RepsRPESet

    @staticmethod
    def create_set(reps: int, rpe: int) -> RepsSet:
        return RepsRPESet(reps=reps, rpe=rpe)

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...


class RepsAndWeightsExercise(RepsExercise):
    set_class = RepsAndWeightsSet

    @staticmethod
    def create_set(
        reps: int,
        weight: float | None = None,
        percentage: float | None = None,
        relative_percentage: float | None = None,
    ) -> RepsAndWeightsSet:
        return RepsAndWeightsSet(
            reps=reps,
            weight=weight,
            relative_percentage=relative_percentage,
            percentage=percentage,
        )

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...


class OlyWeightLiftingExercise(RepsExercise):
    set_class = OlyWeightLiftingSet

    @staticmethod
    def create_set(
        reps: int,
        weight: float | None = None,
        percentage: float | None = None,
    ) -> OlyWeightLiftingSet:
        return OlyWeightLiftingSet(
            reps=reps,
            weight=weight,
            percentage=percentage,
        )

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...


class DurationExercise(Exercise):
    set_class = DurationSet

    @staticmethod
    def create_set(duration: time) -> DurationSet:
        return DurationSet(duration=duration)

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...
