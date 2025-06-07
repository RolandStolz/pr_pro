from pr_pro.configs import ComputeConfig
from pr_pro.functions import Brzycki1RMCalculator
from pr_pro.program import Program


def test_simple_plan_creation(simple_example_program: Program):
    simple_example_program.compute_values(
        compute_config=ComputeConfig(one_rm_calculator=Brzycki1RMCalculator())
    )
    print(simple_example_program)


def test_example_plan_creation(example_program: Program):
    example_program.compute_values(
        compute_config=ComputeConfig(one_rm_calculator=Brzycki1RMCalculator())
    )
    print(example_program)


def test_json_serialization_simple(simple_example_program: Program, tmp_path):
    simple_example_program.write_json_file(tmp_path.joinpath('simple_program.json'))
    loaded_simple_example_program = Program.from_json_file(tmp_path.joinpath('simple_program.json'))

    assert simple_example_program == loaded_simple_example_program


def test_json_serialization(example_program: Program, tmp_path):
    example_program.write_json_file(tmp_path.joinpath('program.json'))
    loaded_example_program = Program.from_json_file(tmp_path.joinpath('program.json'))

    assert example_program == loaded_example_program
