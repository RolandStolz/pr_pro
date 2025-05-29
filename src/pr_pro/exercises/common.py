from pr_pro.exercise import RepsExercise
from pr_pro.exercise import RepsAndWeightsExercise
from pr_pro.exercises.registry import register_exercise


pullup = RepsExercise(name='Pullup')
register_exercise(pullup)
pushup = RepsExercise(name='Pushup')
register_exercise(pushup)

backsquat = RepsAndWeightsExercise(name='Backsquat')
register_exercise(backsquat)
deadlift = RepsAndWeightsExercise(name='Deadlift')
register_exercise(deadlift)
bench_press = RepsAndWeightsExercise(name='Bench Press')
register_exercise(bench_press)
split_squat = RepsAndWeightsExercise(name='Split Squat')
register_exercise(split_squat)
row = RepsAndWeightsExercise(name='Row')
register_exercise(row)

pendlay_row = RepsAndWeightsExercise(name='Pendlay Row')
register_exercise(pendlay_row)
hip_thrust = RepsAndWeightsExercise(name='Hip Thrust')
register_exercise(hip_thrust)


if __name__ == '__main__':
    print(pullup.model_dump())
