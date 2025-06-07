import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# Source: https://www.vcalc.com/wiki/brzycki, https://www.vcalc.com/wiki/body-building-weight-lifting-calculator


@runtime_checkable
@dataclass(frozen=True)
class OneRMCalculator(Protocol):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float: ...
    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float: ...
    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float: ...


@dataclass(frozen=True)
class Epley1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (1 + reps / 30)

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight / (1 + reps / 30)

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return 30 * (one_rm_weight / weight - 1)


@dataclass(frozen=True)
class Brzycki1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * 36 / (37 - reps)

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight * (37 - reps) / 36

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return 37 - 36 * weight / one_rm_weight
        # return 37 - 36 * (one_rm_weight / weight)


@dataclass(frozen=True)
class Landers1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (100 / (101.3 - 2.67123 * reps))

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight * (101.3 - 2.67123 * reps) / 100

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return (101.3 - 100 * weight / one_rm_weight) / 2.67123


@dataclass(frozen=True)
class Lombardi1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (reps**0.10)

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight / (reps**0.10)

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return one_rm_weight / weight**10


@dataclass(frozen=True)
class OConner1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (1 + reps / 40)

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight / (1 + reps / 40)

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return 40 * (one_rm_weight / weight - 1)


@dataclass(frozen=True)
class Wathan1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (100 / (48.8 + 53.8 * (reps**-0.075)))

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight * (48.8 + 53.8 * (reps**-0.075)) / 100

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return -0.075 * (48.8 - 100 * weight / one_rm_weight) ** -1


@dataclass(frozen=True)
class Mayhew1RMCalculator(OneRMCalculator):
    @staticmethod
    def one_rep_max(weight: float, reps: float) -> float:
        return weight * (100 / (52.2 + 41.9 * (math.exp(-0.055 * reps))))

    @staticmethod
    def max_weight_from_reps(one_rm_weight: float, reps: float) -> float:
        return one_rm_weight * (52.2 + 41.9 * (math.exp(-0.055 * reps))) / 100

    @staticmethod
    def max_reps_from_weight(one_rm_weight: float, weight: float) -> float:
        return -1 / 0.055 * math.log((52.2 - 100 * weight / one_rm_weight) / 41.9)
