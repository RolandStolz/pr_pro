from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise_t
from pr_pro.workout_component import SingleExercise, WorkoutComponent_t


from pydantic import BaseModel


from typing import Self


class WorkoutSession(BaseModel):
    id: str
    notes: str | None = None
    workout_components: list[WorkoutComponent_t] = []

    def __str__(self):
        notes_str = f'notes: {self.notes}\n' if self.notes else ''
        return (
            f'--- {self.id} ---\n'
            + notes_str
            + '\n'.join([wc.__str__() for wc in self.workout_components])
            + '\n'
        )

    def add_component(self, workout_component: WorkoutComponent_t) -> Self:
        self.workout_components.append(workout_component)
        return self

    def add_co(self, workout_component: WorkoutComponent_t) -> Self:
        return self.add_component(workout_component)

    def add_single_exercise(self, exercise: Exercise_t) -> Self:
        component = SingleExercise(exercise=exercise)
        self.add_component(component)
        return self

    def add_se(self, exercise: Exercise_t) -> Self:
        return self.add_single_exercise(exercise)

    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None:
        for component in self.workout_components:
            component.compute_values(best_exercise_values, compute_config)
