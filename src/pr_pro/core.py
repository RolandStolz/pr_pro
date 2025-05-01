from pydantic import BaseModel

from pr_pro.exercise import Exercise
from pr_pro.workout_component import WorkoutComponent


class WorkoutSession(BaseModel):
    workout_components: list[WorkoutComponent]


class Program(BaseModel):
    best_exercise_values: dict[Exercise, float]
    workout_sessions: list[WorkoutSession]
