from abc import abstractmethod, ABC
import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator

from pr_pro.sets import (
    DurationSet,
    PowerExerciseSet,
    RepsAndWeightsSet,
    RepsDistanceSet,
    RepsRPESet,
    RepsSet,
    WorkingSet,
    WorkingSet_t,
)


class Exercise(BaseModel, ABC):
    set_class: ClassVar[type[WorkingSet_t]]
    name: str
    # Necessary for discerning exercises in model validation
    model_type: Literal['Exercise'] = 'Exercise'
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
            exercise_class = get_exercise_type_by_key_string(data)
            name = data.split('(')[0].strip()
            return exercise_class(name=name).model_dump()

        return data


class RepsExercise(Exercise):
    set_class = RepsSet
    model_type: Literal['RepsExercise'] = 'RepsExercise'

    @staticmethod
    def create_set(reps: int) -> RepsSet:
        return RepsSet(reps=reps)

    if TYPE_CHECKING:  # pragma: no cover

        def __hash__(self) -> int: ...


class RepsRPEExercise(RepsExercise):
    set_class = RepsRPESet
    model_type: Literal['RepsRPEExercise'] = 'RepsRPEExercise'

    @staticmethod
    def create_set(reps: int, rpe: int) -> RepsSet:
        return RepsRPESet(reps=reps, rpe=rpe)

    if TYPE_CHECKING:  # pragma: no cover

        def __hash__(self) -> int: ...


class RepsAndWeightsExercise(RepsExercise):
    set_class = RepsAndWeightsSet
    model_type: Literal['RepsAndWeightsExercise'] = 'RepsAndWeightsExercise'

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

    if TYPE_CHECKING:  # pragma: no cover

        def __hash__(self) -> int: ...


class PowerExercise(RepsExercise):
    set_class = PowerExerciseSet
    model_type: Literal['PowerExercise'] = 'PowerExercise'

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

    if TYPE_CHECKING:  # pragma: no cover

        def __hash__(self) -> int: ...


class RepsDistanceExercise(RepsExercise):
    set_class = RepsDistanceSet
    model_type: Literal['RepsDistanceExercise'] = 'RepsDistanceExercise'

    @staticmethod
    def create_set(reps: int, distance: float) -> RepsDistanceSet:
        return RepsDistanceSet(reps=reps, distance=distance)


class DurationExercise(Exercise):
    set_class = DurationSet
    model_type: Literal['DurationExercise'] = 'DurationExercise'

    @staticmethod
    def create_set(duration: datetime.timedelta) -> DurationSet:
        return DurationSet(duration=duration)

    if TYPE_CHECKING:  # pragma: no cover

        def __hash__(self) -> int: ...


# The type union is required for correct pydantic model validation
Exercise_t = (
    RepsExercise | RepsRPEExercise | RepsAndWeightsExercise | PowerExercise | DurationExercise
)


def get_exercise_type_by_key_string(key: str) -> type[Exercise]:
    type_name = key.split('(')[-1].split(')')[0]
    type_dict = {
        'RepsExercise': RepsExercise,
        'RepsRPEExercise': RepsRPEExercise,
        'RepsAndWeightsExercise': RepsAndWeightsExercise,
        'PowerExercise': PowerExercise,
        'DurationExercise': DurationExercise,
    }
    if type_name not in type_dict:
        raise ValueError(f'Unknown exercise type: {type_name}')
    return type_dict[type_name]


if __name__ == '__main__':  # pragma: no cover
    test = PowerExercise(name='test')
    print(test.model_dump())
