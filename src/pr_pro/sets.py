from __future__ import annotations

import datetime
import logging
from typing import Any, Callable

import pandas as pd
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


MetricConfig = tuple[str, str, Callable[[Any], Any] | None]

METRIC_CONFIGS: dict[type[WorkingSet_t], list[MetricConfig]] = {
    RepsAndWeightsSet: [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
        ('relative_percentage', 'Rel %', lambda rp: f'{rp * 100:.0f}%'),
    ],
    RepsRPESet: [
        ('reps', 'Reps', None),
        ('rpe', 'RPE', None),
    ],
    PowerExerciseSet: [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
    ],
    RepsSet: [
        ('reps', 'Reps', None),
    ],
    DurationSet: [
        (
            'duration',
            'Duration',
            lambda d: d.strftime('%M:%S') if hasattr(d, 'strftime') else str(d),
        ),
    ],
}


def _get_metric_config(set_instance: WorkingSet_t) -> list[MetricConfig]:
    """
    Gets the metric configuration for a given set instance by checking its type.
    The order of checks is important due to class inheritance.
    """
    for set_type, config in METRIC_CONFIGS.items():
        if isinstance(set_instance, set_type):
            return config
    return []


def _build_metrics_list(ws: WorkingSet_t, configs: list[MetricConfig]) -> list[tuple[str, Any]]:
    """
    Builds a list of metrics from a working set based on configurations.

    Args:
        ws: The working set object.
        configs: A list of tuples, where each tuple contains:
                 (attribute_name, display_label, optional_formatter_function)
    """
    metrics = []
    for attr_name, label, formatter in configs:
        if hasattr(ws, attr_name):
            value = getattr(ws, attr_name)
            if value is not None:  # Ensure attribute has a meaningful value
                display_value = formatter(value) if formatter else value
                metrics.append((label, display_value))
    return metrics


def create_sets_dataframe(_sets: list[WorkingSet_t]) -> pd.DataFrame:
    """
    Creates a DataFrame of metrics for a list of working sets of the same type.

    Args:
        sets: A list of working set objects, all expected to be of the same type.

    Returns:
        A pandas DataFrame where each row represents a set and each column a metric.
    """
    if not _sets:
        return pd.DataFrame()

    first_set = _sets[0]
    configs = _get_metric_config(first_set)

    if not configs:
        return pd.DataFrame([str(s) for s in _sets], columns=['Set Details'])

    all_set_metrics = []
    for i, ws in enumerate(_sets):
        metrics_list = _build_metrics_list(ws, configs)
        metrics_dict = {'Set': i + 1}
        # metrics_dict = {label: value for label, value in metrics_list}
        for label, value in metrics_list:
            metrics_dict[label] = value

        all_set_metrics.append(metrics_dict)

    df = pd.DataFrame(all_set_metrics)
    cols = ['Set'] + [col for col in df.columns if col != 'Set']
    df = df[cols]

    if first_set.rest_between is not None:
        rest_times = [getattr(s, 'rest_between', None) for s in _sets]
        df['Rest'] = rest_times

    return df
