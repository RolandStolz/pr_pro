from __future__ import annotations

import enum
from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkingSet(BaseModel):
    repititions: int


class Exercise(BaseModel):
    set_class: ClassVar[type[WorkingSet]] = WorkingSet
    name: str
    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def create_set(self, repititions: int) -> WorkingSet: ...

    if TYPE_CHECKING:
        # For pylance
        def __hash__(self) -> int: ...


class WeightType(enum.StrEnum):
    bodyweight = 'bodyweight'


class RepsAndWeightsSet(WorkingSet):
    weight: float | WeightType | None = Field(default=None, ge=0)
    relative_percentage: float | None = Field(default=None, ge=0)
    absolute_percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(
            data.get(field) is not None
            for field in ['weight', 'relative_percentage', 'absolute_percentage']
        ):
            raise ValueError(
                'At least one of weight, relative_percentage, or absolute_percentage must be provided.'
            )
        return data


class RepsAndWeightsExercise(Exercise):
    set_class = RepsAndWeightsSet

    @staticmethod
    def create_set(
        repititions: int,
        weight: float | WeightType | None = None,
        relative_percentage: float | None = None,
        absolute_percentage: float | None = None,
    ) -> RepsAndWeightsSet:
        return RepsAndWeightsSet(
            repititions=repititions,
            weight=weight,
            relative_percentage=relative_percentage,
            absolute_percentage=absolute_percentage,
        )

    if TYPE_CHECKING:
        # For pylance
        def __hash__(self) -> int: ...


class OlyWeightLiftingSet(WorkingSet):
    weight: float | WeightType | None = Field(default=None, ge=0)
    absolute_percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(data.get(field) is not None for field in ['weight', 'absolute_percentage']):
            raise ValueError('At least one of weight, or absolute_percentage must be provided.')
        return data


class OlyWeightLiftingExercise(Exercise):
    set_class = OlyWeightLiftingSet

    @staticmethod
    def create_set(
        repititions: int,
        weight: float | WeightType | None = None,
        absolute_percentage: float | None = None,
    ) -> OlyWeightLiftingSet:
        return OlyWeightLiftingSet(
            repititions=repititions,
            weight=weight,
            absolute_percentage=absolute_percentage,
        )

    if TYPE_CHECKING:
        # For pylance
        def __hash__(self) -> int: ...


if __name__ == '__main__':
    test = OlyWeightLiftingExercise(name='Snatch').create_set(repititions=2, weight=60)
    print(test)
