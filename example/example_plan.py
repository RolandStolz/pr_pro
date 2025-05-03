from pr_pro.core import Program, WorkoutSession
from pr_pro.exercises.common import backsquat, deadlift, bench_press, row
from pr_pro.workout_component import SingleExercise


def main():
    program = (
        Program(name='Test program')
        .add_best_exercise(backsquat, 55)
        .add_best_exercise(deadlift, 90)
        .add_best_exercise(bench_press, 50)
    )
    program.add_best_exercise(row, program.best_exercise_values[deadlift] * 0.6)

    session1 = WorkoutSession(id='W1D1').add_component(
        SingleExercise(exercise=backsquat).add_repeating_set(
            4, backsquat.create_set(repititions=10, weight=80)
        )
    )
    program.add_workout_session(session1)

    session2 = WorkoutSession(id='W1D2').add_component(
        SingleExercise(exercise=backsquat).add_repeating_set(
            4, backsquat.create_set(repititions=10, weight=90)
        )
    )
    program.add_workout_session(session2)

    print(program)


if __name__ == '__main__':
    main()
