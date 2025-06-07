import pytest
from pr_pro.configs import ComputeConfig
from pr_pro.functions import (
    Epley1RMCalculator,
    Brzycki1RMCalculator,
    Landers1RMCalculator,
    Lombardi1RMCalculator,
    OConner1RMCalculator,
    Wathan1RMCalculator,
    Mayhew1RMCalculator,
    OneRMCalculator,
)
from pr_pro.program import Program

CALCULATOR_CLASSES = [
    Epley1RMCalculator,
    Brzycki1RMCalculator,
    Landers1RMCalculator,
    Lombardi1RMCalculator,
    OConner1RMCalculator,
    Wathan1RMCalculator,
    Mayhew1RMCalculator,
]


@pytest.mark.parametrize('calculator_class', CALCULATOR_CLASSES)
def test_compute_values_simple_plan(
    calculator_class: OneRMCalculator, simple_example_program: Program
):
    simple_example_program.compute_values(
        compute_config=ComputeConfig(one_rm_calculator=calculator_class)
    )
    print(f'Computed program with {calculator_class}:\n{simple_example_program}')


@pytest.mark.parametrize('calculator_class', CALCULATOR_CLASSES)
def test_compute_values_example_plan(calculator_class: OneRMCalculator, example_program: Program):
    example_program.compute_values(compute_config=ComputeConfig(one_rm_calculator=calculator_class))
    print(f'Computed program with {calculator_class}:\n{example_program}')
