from pr_pro.exercise import PowerExercise, RepsExercise
from pr_pro.exercise import RepsAndWeightsExercise


pullup = RepsExercise(name='Pullup')
pushup = RepsExercise(name='Pushup')

power_clean = PowerExercise(name='Power Clean')

backsquat = RepsAndWeightsExercise(name='Backsquat')
deadlift = RepsAndWeightsExercise(name='Deadlift')
bench_press = RepsAndWeightsExercise(name='Bench Press')
split_squat = RepsAndWeightsExercise(name='Split Squat')
row = RepsAndWeightsExercise(name='Row')

pendlay_row = RepsAndWeightsExercise(name='Pendlay Row')
hip_thrust = RepsAndWeightsExercise(name='Hip Thrust')


if __name__ == '__main__':  # pragma: no cover
    print(pullup.model_dump())
