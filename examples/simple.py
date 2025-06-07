from pr_pro.configs import ComputeConfig
from pr_pro.example import get_simple_example_program
from pr_pro.functions import Brzycki1RMCalculator


def main():
    program = get_simple_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))
    print(program)


if __name__ == '__main__':
    main()
