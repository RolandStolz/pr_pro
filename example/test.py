from pathlib import Path
from pr_pro.workout_session import WorkoutSession
from pr_pro.configs import ComputeConfig
from pr_pro.program import Program
from pr_pro.exercise import RepsAndWeightsExercise
from pr_pro.exercises.common import backsquat, pushup
from pr_pro.workout_component import SingleExercise, ExerciseGroup


def main():
    pendlay_row = RepsAndWeightsExercise(name='Pendlay row').register()

    program = Program(name='Test program').add_best_exercise_value(backsquat, 100)
    program.add_best_exercise_value(pendlay_row, program.best_exercise_values[backsquat] * 0.6)

    w1d1 = (
        WorkoutSession(id='W1D1', notes='Power day.')
        .add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                4, backsquat.create_set(5, percentage=0.55)
            )
        )
        .add_component(
            ExerciseGroup(exercises=[pendlay_row, pushup]).add_repeating_group_sets(
                4,
                {
                    pendlay_row: pendlay_row.create_set(6, percentage=0.6),
                    pushup: pushup.create_set(10),
                },
            )
        )
        .add_component(
            SingleExercise(exercise=pendlay_row).add_repeating_set(
                4, pendlay_row.create_set(6, percentage=0.6)
            )
        )
    )

    program.add_workout_session(w1d1)
    program.compute_values(ComputeConfig())

    program.write_json_file(Path('test.json'))

    loaded = Program.from_json_file(Path('test.json'))
    print(loaded)


if __name__ == '__main__':
    main()
