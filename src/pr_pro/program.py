from typing import Self

from pydantic import BaseModel

from pr_pro.workout_session import WorkoutSession
from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise


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
        if workout_session.id in [ws.id for ws in self.workout_sessions]:
            raise ValueError(
                f'Workout session id must be unique. {workout_session.id} already exists.'
            )
        self.workout_sessions.append(workout_session)
        return self

    def add_best_exercise_value(self, exercise: Exercise, value: float) -> Self:
        self.best_exercise_values[exercise] = value
        return self

    def compute_program(self, compute_config: ComputeConfig) -> None:
        for session in self.workout_sessions:
            session.compute_session(self.best_exercise_values, compute_config)
