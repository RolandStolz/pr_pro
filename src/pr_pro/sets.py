from __future__ import annotations

import datetime
import logging

from pydantic import BaseModel, Field, model_validator
from pr_pro.configs import ComputeConfig

logger = logging.getLogger(__name__)


class WorkingSet(BaseModel):
    rest_between: datetime.timedelta | None = None

    def __str__(self) -> str:
        formatted_items = []
        for a, value in self.model_dump().items():
            if value is not None:
                if isinstance(value, float):
                    formatted_items.append(f'{a} {round(value, 3)}')
                else:
                    formatted_items.append(f'{a} {value}')
        return ', '.join(formatted_items)

    def compute_values(self, best_exercise_value: float, compute_config: ComputeConfig) -> None:
        # A lot of set types cannot compute values, hence they don't have to redefine the method
        pass


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

    def compute_values(self, best_exercise_value: float, compute_config: ComputeConfig) -> None:
        tol = 1e-6

        if self.weight is not None:
            if self.percentage is None:
                self.percentage = self.weight / best_exercise_value
            else:
                assert self.percentage - self.weight / best_exercise_value <= tol, (
                    f'Missmatch between provided percentage {self.percentage} and '
                    f'weight {self.weight} and best exercise value {best_exercise_value}.'
                )

        if self.percentage is not None:
            if self.weight is None:
                self.weight = best_exercise_value * self.percentage
            else:
                assert self.weight - best_exercise_value * self.percentage <= tol, (
                    f'Missmatch between provided weight {self.weight} and '
                    f'percentage {self.percentage} and best exercise value {best_exercise_value}.'
                )

        if self.relative_percentage is not None:
            weight = (
                self.relative_percentage
                * compute_config.one_rm_calculator.max_weight_from_reps(
                    best_exercise_value, self.reps
                )
            )
            percentage = weight / best_exercise_value

            assert self.weight is None or self.weight - weight <= tol, (
                f'Missmatch between provided weight {self.weight} and computed weight {weight}.'
            )
            assert self.percentage is None or self.percentage - percentage <= tol, (
                f'Missmatch between provided percentage {self.percentage} and computed percentage {percentage}.'
            )
            self.weight = weight
            self.percentage = percentage
        else:
            assert self.weight is not None
            self.relative_percentage = (
                compute_config.one_rm_calculator.one_rep_max(self.weight, self.reps)
                / best_exercise_value
            )

        assert self.weight is not None
        assert self.percentage is not None
        assert self.relative_percentage is not None


class PowerExerciseSet(RepsSet):
    weight: float | None = Field(default=None, ge=0)
    percentage: float | None = Field(default=None, ge=0)

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_weight(cls, data):
        if not any(data.get(field) is not None for field in ['weight', 'percentage']):
            raise ValueError('At least one of weight, or percentage must be provided.')
        return data

    def compute_values(self, best_exercise_value: float, compute_config: ComputeConfig) -> None:
        tol = 1e-6

        if self.weight is not None:
            if self.percentage is None:
                self.percentage = self.weight / best_exercise_value
            else:
                assert self.percentage - best_exercise_value / self.weight <= tol, (
                    f'Missmatch between provided percentage {self.percentage} and '
                    f'weight {self.weight} and best exercise value {best_exercise_value}.'
                )

        if self.percentage is not None:
            if self.weight is None:
                self.weight = best_exercise_value * self.percentage
            else:
                assert self.weight - best_exercise_value * self.percentage <= tol, (
                    f'Missmatch between provided weight {self.weight} and '
                    f'percentage {self.percentage} and best exercise value {best_exercise_value}.'
                )

        assert self.weight is not None
        assert self.percentage is not None


class RepsDistanceSet(RepsSet):
    distance: float


class DurationSet(WorkingSet):
    duration: datetime.timedelta


WorkingSet_t = RepsSet | RepsRPESet | RepsAndWeightsSet | PowerExerciseSet | DurationSet
