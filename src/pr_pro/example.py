import datetime

from pr_pro.exercise import DurationExercise, RepsAndWeightsExercise, RepsExercise, RepsRPEExercise
from pr_pro.exercises.common import backsquat, bench_press, deadlift, pullup, pushup, split_squat
from pr_pro.program import Program
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import (
    WorkoutSession,
    exercise_group_from_prev_session,
    single_exercise_from_prev_session,
)


def get_simple_example_program() -> Program:
    pendlay_row = RepsAndWeightsExercise(name='Pendlay row')

    program = (
        Program(name='Test program')
        .add_best_exercise_value(backsquat, 100)
        .add_best_exercise_value(bench_press, 80)
    )

    w1d1 = (
        WorkoutSession(id='W1D1', notes='Easy on first day.')
        .add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                2, backsquat.create_set(5, percentage=0.55)
            )
        )
        .add_component(
            ExerciseGroup(exercises=[pendlay_row, pushup]).add_repeating_group_sets(
                2,
                {
                    pendlay_row: pendlay_row.create_set(6, percentage=0.6),
                    pushup: pushup.create_set(10),
                },
            )
        )
        .add_component(
            SingleExercise(exercise=bench_press).add_repeating_set(
                2, bench_press.create_set(8, percentage=0.5)
            )
        )
    )

    program.add_workout_session(w1d1)
    return program


def get_example_program() -> Program:
    box_jump = RepsExercise(name='Box jump')
    pendlay_row = RepsAndWeightsExercise(name='Pendlay row')
    dumbbell_shoulder_press = RepsRPEExercise(name='Dumbbell shoulder press')
    hip_thrust = RepsAndWeightsExercise(name='Hip thrust')
    side_plank_leg_raise = RepsExercise(name='Side plank leg raise')
    cable_pulldown = RepsRPEExercise(name='Straight arm cable pulldown')
    pallov_press = RepsRPEExercise(name='Pallov press')
    squat_hold = DurationExercise(name='Squat hold')
    hanging_knee_raise = RepsAndWeightsExercise(name='Hanging knee raise')
    reverse_hyperextension = RepsExercise(name='Reverse hyperextension')

    program = (
        Program(name='Test program')
        .add_best_exercise_value(backsquat, 55)
        .add_best_exercise_value(deadlift, 90)
        .add_best_exercise_value(bench_press, 50)
    )
    program.add_best_exercise_value(pendlay_row, program.best_exercise_values[deadlift] * 0.6)

    w1d1 = (
        WorkoutSession(id='W1D1', notes='Power day.')
        .add_component(
            SingleExercise(exercise=box_jump, notes='Good warmup please!').add_repeating_set(
                5, box_jump.create_set(4)
            )
        )
        .add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                4, backsquat.create_set(5, percentage=0.55)
            )
        )
        .add_component(
            ExerciseGroup(
                exercises=[pendlay_row, dumbbell_shoulder_press],
                notes='Put down completely for pendlay row.',
            ).add_repeating_group_sets(
                4,
                {
                    pendlay_row: pendlay_row.create_set(6, percentage=0.6),
                    dumbbell_shoulder_press: dumbbell_shoulder_press.create_set(10, rpe=6),
                },
            )
        )
        .add_component(
            ExerciseGroup(exercises=[hip_thrust, side_plank_leg_raise]).add_repeating_group_sets(
                4,
                {
                    hip_thrust: hip_thrust.create_set(8, weight=60),
                    side_plank_leg_raise: side_plank_leg_raise.create_set(10),
                },
            )
        )
    )
    program.add_workout_session(w1d1)

    w1d2 = (
        WorkoutSession(id='W1D2')
        .add_component(
            SingleExercise(exercise=deadlift, notes='Squeeze glutes!').add_repeating_set(
                3, deadlift.create_set(12, percentage=0.5)
            )
        )
        .add_component(
            SingleExercise(exercise=split_squat).add_repeating_set(
                4, backsquat.create_set(6, weight=0)
            )
        )
        .add_component(
            ExerciseGroup(
                exercises=[pullup, pushup], notes='Pullup with reverse grip'
            ).add_repeating_group_sets(
                5,
                {pullup: pullup.create_set(1), pushup: pushup.create_set(6)},
            )
        )
        .add_component(
            ExerciseGroup(exercises=[cable_pulldown, pallov_press]).add_repeating_group_sets(
                4,
                {
                    cable_pulldown: cable_pulldown.create_set(10, rpe=6),
                    pallov_press: pallov_press.create_set(10, rpe=6),
                },
            )
        )
    )
    program.add_workout_session(w1d2)

    w1d3 = (
        WorkoutSession(id='W1D3')
        .add_component(
            SingleExercise(exercise=squat_hold).add_repeating_set(
                3, squat_hold.create_set(duration=datetime.timedelta(minutes=1))
            )
        )
        .add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                4, backsquat.create_set(8, percentage=0.6)
            )
        )
        .add_component(
            SingleExercise(exercise=deadlift, notes='Every minute on the minute').add_repeating_set(
                10, deadlift.create_set(2, percentage=0.5)
            )
        )
        .add_component(
            SingleExercise(exercise=bench_press).add_repeating_set(
                4, bench_press.create_set(10, percentage=0.6)
            )
        )
        .add_component(
            ExerciseGroup(
                exercises=[hanging_knee_raise, reverse_hyperextension]
            ).add_repeating_group_sets(
                4,
                {
                    hanging_knee_raise: hanging_knee_raise.create_set(6, weight=10),
                    reverse_hyperextension: reverse_hyperextension.create_set(6),
                },
            )
        )
    )
    program.add_workout_session(w1d3)

    w2d1 = (
        WorkoutSession(id='W2D1')
        .add_component(single_exercise_from_prev_session(w1d1, box_jump, reps=+1))
        .add_component(single_exercise_from_prev_session(w1d1, backsquat, percentage=+0.1))
        .add_component(
            exercise_group_from_prev_session(
                w1d1,
                [pendlay_row, dumbbell_shoulder_press],
                percentage=(+0.05, None),
                rpe=(None, +1),
            )
        )
        .add_component(exercise_group_from_prev_session(w1d1, [hip_thrust, side_plank_leg_raise]))
    )
    program.add_workout_session(w2d1)

    w2d2 = (
        WorkoutSession(id='W2D2')
        .add_component(single_exercise_from_prev_session(w1d2, deadlift, percentage=+0.05, reps=-2))
        .add_component(single_exercise_from_prev_session(w1d2, split_squat, weight=+10))
        .add_component(exercise_group_from_prev_session(w1d2, [pullup, pushup], reps=(+1, +1)))
        .add_component(
            exercise_group_from_prev_session(w1d2, [cable_pulldown, pallov_press], rpe=(+1, +1))
        )
    )
    program.add_workout_session(w2d2)

    w2d3 = (
        WorkoutSession(id='W2D3')
        .add_component(
            single_exercise_from_prev_session(
                w1d3, squat_hold, duration=datetime.timedelta(seconds=30)
            )
        )
        .add_component(single_exercise_from_prev_session(w1d3, backsquat, percentage=+0.1))
        .add_component(single_exercise_from_prev_session(w1d3, deadlift, percentage=+0.05))
        .add_component(single_exercise_from_prev_session(w1d3, bench_press, percentage=+0.05))
        .add_component(
            exercise_group_from_prev_session(
                w1d3, [hanging_knee_raise, reverse_hyperextension], weight=(+5, None)
            )
        )
    )
    program.add_workout_session(w2d3)

    program.add_program_phase('W1', [w1d1.id, w1d2.id, w1d3.id])
    program.add_program_phase('W2', [w2d1.id, w2d2.id, w2d3.id])

    return program


if __name__ == '__main__':  # pragma: no cover
    program = get_example_program()
    print(program)
