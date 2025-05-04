from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from datetime import time


class WorkingSet(BaseModel):
    rest_between: time | None = None

    def __str__(self) -> str:
        return ', '.join(
            [f'{a} {value}' for a, value in self.model_dump().items() if value is not None]
        )


class RepsSet(WorkingSet):
    reps: int


class RepsRPESet(RepsSet):
    rpe: int


class RepsAndWeightsSet(RepsSet):
    weight: float | None = Field(default=None, ge=0)
    percentage: float | None = Field(default=None, ge=0)
    relative_percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(
            data.get(field) is not None for field in ['weight', 'relative_percentage', 'percentage']
        ):
            raise ValueError(
                'At least one of weight, relative_percentage, or percentage must be provided.'
            )
        return data


class OlyWeightLiftingSet(RepsSet):
    weight: float | None = Field(default=None, ge=0)
    percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(data.get(field) is not None for field in ['weight', 'percentage']):
            raise ValueError('At least one of weight, or percentage must be provided.')
        return data


class DurationSet(WorkingSet):
    duration: time
