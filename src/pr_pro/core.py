from typing import Self
from pydantic import BaseModel

from pr_pro.sets import Exercise
from pr_pro.workout_component import WorkoutComponent


class WorkoutSession(BaseModel):
    id: str
    workout_components: list[WorkoutComponent] = []

    def __str__(self):
        return f'--- {self.id} ---\n' + '\n'.join([wc.__str__() for wc in self.workout_components]) + '\n'

    def add_component(self, workout_component: WorkoutComponent) -> Self:
        self.workout_components.append(workout_component)
        return self


class Program(BaseModel):
    name: str
    best_exercise_values: dict[Exercise, float] = {}
    workout_sessions: list[WorkoutSession] = []

    def __str__(self) -> str:
        workout_str = f'--- Workout {self.name} ---\n'
        best_exercise_str = (
            'Best exercise values\n  '
            + '\n  '.join([f'{e.name}: {value}' for e, value in self.best_exercise_values.items()])
            + '\n\n'
        )
        workout_sessions_str = (
            'Workout sessions\n' + '\n'.join(ws.__str__() for ws in self.workout_sessions) + '\n'
        )
        return workout_str + best_exercise_str + workout_sessions_str

    def add_workout_session(self, workout_session: WorkoutSession) -> Self:
        self.workout_sessions.append(workout_session)
        return self

    def add_best_exercise(self, exercise: Exercise, value: float) -> Self:
        self.best_exercise_values[exercise] = value
        return self
