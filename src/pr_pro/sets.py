from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkingSet(BaseModel):
    rest_between: int | None = None

    def __str__(self) -> str:
        return ', '.join(
            [f'{a} {value}' for a, value in self.model_dump().items() if value is not None]
        )


class Exercise(BaseModel):
    set_class: ClassVar[type[WorkingSet]] = WorkingSet
    name: str
    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def create_set(self, reps: int) -> WorkingSet: ...

    if TYPE_CHECKING:
        # For pylance
        def __hash__(self) -> int: ...


class RepsSet(WorkingSet):
    reps: int


class RepsExercise(Exercise):
    set_class = RepsSet

    @staticmethod
    def create_set(reps: int) -> RepsSet:
        return RepsSet(reps=reps)

    if TYPE_CHECKING:

        def __hash__(self) -> int: ...


class RepsAndWeightsSet(RepsSet):
    weight: float | None = Field(default=None, ge=0)
    percentage: float | None = Field(default=None, ge=0)
    relative_percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(
            data.get(field) is not None
            for field in ['weight', 'relative_percentage', 'percentage']
        ):
            raise ValueError(
                'At least one of weight, relative_percentage, or percentage must be provided.'
            )
        return data


class RepsAndWeightsExercise(Exercise):
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


class OlyWeightLiftingSet(RepsSet):
    weight: float | None = Field(default=None, ge=0)
    percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(data.get(field) is not None for field in ['weight', 'percentage']):
            raise ValueError('At least one of weight, or percentage must be provided.')
        return data


class OlyWeightLiftingExercise(Exercise):
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


if __name__ == '__main__':
    test = OlyWeightLiftingExercise(name='Snatch').create_set(reps=2, weight=60)
    print(test)
