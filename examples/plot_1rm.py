import matplotlib.pyplot as plt
import numpy as np

from pr_pro.functions import (
    Brzycki1RMCalculator,
    Epley1RMCalculator,
    Landers1RMCalculator,
    Lombardi1RMCalculator,
    Mayhew1RMCalculator,
    OConner1RMCalculator,
    OneRMCalculator,
    Wathan1RMCalculator,
)


def main():
    reps = np.arange(1, 21)
    one_rm_weight = 100

    calculators: dict[str, type[OneRMCalculator]] = {
        'Epley': Epley1RMCalculator,
        'Brzycki': Brzycki1RMCalculator,
        'Landers': Landers1RMCalculator,
        'Lombardi': Lombardi1RMCalculator,
        "O'Conner": OConner1RMCalculator,
        'Wathan': Wathan1RMCalculator,
        'Mayhew': Mayhew1RMCalculator,
    }

    plt.figure()

    for name, calculator in calculators.items():
        weights = [calculator.one_rep_max(one_rm_weight, float(r)) for r in reps]
        plt.plot(reps, weights, label=name)

    plt.xlabel('Reps')
    plt.ylabel('Estimated 1RM')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
