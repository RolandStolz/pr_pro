from abc import abstractmethod, ABC
from datetime import time
from typing import TYPE_CHECKING, Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, ValidationInfo, computed_field, model_validator

from pr_pro.exercises.registry import get_exercise_by_key_string
from pr_pro.sets import (
    DurationSet,
    PowerExerciseSet,
    RepsAndWeightsSet,
    RepsRPESet,
    RepsSet,
    WorkingSet,
    WorkingSet_t,
)


class Exercise(BaseModel, ABC):
    set_class: ClassVar[type[WorkingSet_t]]
    name: str
    model_config = ConfigDict(frozen=True)

    @staticmethod
    @abstractmethod
    def create_set(reps: int) -> WorkingSet: ...

    def __str__(self) -> str:
        return f'{self.name} ({self.__class__.__name__})'

    @model_validator(mode='before')
    @classmethod
    def _validate_from_key_string_or_dict(cls, data: Any, info: ValidationInfo) -> Any:
        if isinstance(data, str):
            return get_exercise_by_key_string(data).model_dump()

        return data

    def register(self) -> Self:
        """
        Registers the exercise in the registry.
        Calling the method is only necessary, if you intent to load a program from a file.
        """
        from pr_pro.exercises.registry import register_exercise

        register_exercise(self)
        return self


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


class PowerExercise(RepsExercise):
    set_class = PowerExerciseSet

    @staticmethod
    def create_set(
        reps: int,
        weight: float | None = None,
        percentage: float | None = None,
    ) -> PowerExerciseSet:
        return PowerExerciseSet(
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


Exercise_t = (
    RepsExercise | RepsRPEExercise | RepsAndWeightsExercise | PowerExercise | DurationExercise
)

if __name__ == '__main__':
    test = PowerExercise(name='test')
    print(test.model_dump())
