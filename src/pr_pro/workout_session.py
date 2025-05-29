from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise
from pr_pro.workout_component import SingleExercise, WorkoutComponent


from pydantic import BaseModel


from typing import Self


class WorkoutSession(BaseModel):
    id: str
    notes: str | None = None
    workout_components: list[WorkoutComponent] = []

    def __str__(self):
        notes_str = f'notes: {self.notes}\n' if self.notes else ''
        return (
            f'--- {self.id} ---\n'
            + notes_str
            + '\n'.join([wc.__str__() for wc in self.workout_components])
            + '\n'
        )

    def add_component(self, workout_component: WorkoutComponent) -> Self:
        self.workout_components.append(workout_component)
        return self

    def add_co(self, workout_component: WorkoutComponent) -> Self:
        return self.add_component(workout_component)

    def add_single_exercise(self, exercise: Exercise) -> Self:
        component = SingleExercise(exercise=exercise)
        self.add_component(component)
        return self

    def add_se(self, exercise: Exercise) -> Self:
        return self.add_single_exercise(exercise)

    def compute_session(
        self, best_exercise_values: dict[Exercise, float], compute_config: ComputeConfig
    ) -> None:
        for component in self.workout_components:
            component.compute_values(best_exercise_values, compute_config)