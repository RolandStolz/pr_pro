import datetime
from pr_pro.workout_session import WorkoutSession
from pr_pro.configs import ComputeConfig
from pr_pro.program import Program
from pr_pro.exercise import DurationExercise, RepsExercise
from pr_pro.exercises.common import backsquat, deadlift, bench_press, split_squat, pullup, pushup
from pr_pro.exercise import RepsAndWeightsExercise, RepsRPEExercise
from pr_pro.workout_component import ExerciseGroup, SingleExercise


def main():
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

    program.compute_values(compute_config=ComputeConfig())
    print(program)

    # Uncomment to export as pdf
    # from pathlib import Path
    # program.export_to_pdf(Path('test.pdf'))


if __name__ == '__main__':
    main()
