from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise_t
from pr_pro.workout_component import ExerciseGroup, SingleExercise, WorkoutComponent_t


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

    def get_component_by_exercise(self, exercise: Exercise_t) -> SingleExercise | None:
        for component in self.workout_components:
            if isinstance(component, SingleExercise) and component.exercise == exercise:
                return component
        return None

    def get_component_by_exercise_group(self, exercises: list[Exercise_t]) -> ExerciseGroup | None:
        for component in self.workout_components:
            if isinstance(component, ExerciseGroup) and set(component.exercises) == set(exercises):
                return component
        return None

    def add_co(self, workout_component: WorkoutComponent_t) -> Self:
        return self.add_component(workout_component)

    def add_single_exercise(self, exercise: Exercise_t) -> Self:
        component = SingleExercise(exercise=exercise)
        self.add_component(component)
        return self

    def add_se(self, exercise: Exercise_t) -> Self:
        return self.add_single_exercise(exercise)

    def get_number_of_exercises(self) -> int:
        n_exercises = 0
        for component in self.workout_components:
            if isinstance(component, SingleExercise):
                n_exercises += 1
            elif isinstance(component, ExerciseGroup):
                n_exercises += len(component.exercises)
        return n_exercises

    def get_number_of_sets(self) -> int:
        n_sets = 0
        for component in self.workout_components:
            if isinstance(component, SingleExercise):
                n_sets += len(component.sets)
            elif isinstance(component, ExerciseGroup):
                n_sets += sum(len(s) for s in component.exercise_sets_dict.values())
        return n_sets

    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None:
        for component in self.workout_components:
            component.compute_values(best_exercise_values, compute_config)


def single_exercise_from_prev_session(
    previous_session: WorkoutSession, exercise: Exercise_t, **kwargs
) -> SingleExercise:
    """
    Create a SingleExercise component based on a previous session's component.
    """
    prev_component = previous_session.get_component_by_exercise(exercise)
    if not prev_component:
        raise ValueError(f'No previous component found for exercise {exercise.name}.')
    return SingleExercise.from_prev_component(prev_component, **kwargs)


def exercise_group_from_prev_session(
    previous_session: WorkoutSession, exercises: list[Exercise_t], **kwargs
) -> ExerciseGroup:
    """
    Create an ExerciseGroup component based on a previous session's component.
    """
    prev_component = previous_session.get_component_by_exercise_group(exercises)
    if not prev_component:
        raise ValueError(
            f'No previous component found for exercises {", ".join(e.name for e in exercises)}.'
        )
    return ExerciseGroup.from_prev_component(prev_component, **kwargs)
