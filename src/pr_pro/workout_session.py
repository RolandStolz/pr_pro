from collections.abc import Collection
from typing import Self

from pydantic import BaseModel

from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise_t
from pr_pro.sets import WorkingSet_t
from pr_pro.workout_component import ExerciseGroup, SingleExercise, WorkoutComponent_t


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
        return len(self.get_session_sets())

    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None:
        for component in self.workout_components:
            component.compute_values(best_exercise_values, compute_config)

    def get_exercise_sets(self) -> dict[Exercise_t, list[WorkingSet_t]]:
        """Return all working sets in the session, under the exercise they belong to.

        An exercise trained in two components of one session holds the sets of both.
        """
        exercise_sets: dict[Exercise_t, list[WorkingSet_t]] = {}
        for component in self.workout_components:
            component_sets = (
                [(component.exercise, component.sets)]
                if isinstance(component, SingleExercise)
                else list(component.exercise_sets_dict.items())
            )
            for exercise, sets in component_sets:
                exercise_sets.setdefault(exercise, []).extend(sets)
        return exercise_sets

    def get_session_sets(self) -> list[WorkingSet_t]:
        """Return all working sets in the session."""
        return [s for sets in self.get_exercise_sets().values() for s in sets]

    def get_exercise_names(self) -> list[str]:
        """The name of every exercise the session trains, in the order it trains them."""
        return [exercise.name for exercise in self.get_exercise_sets()]

    def filter_exercises(self, exercise_names: Collection[str]) -> Self:
        """A copy of the session holding only the named exercises.

        A group keeps the named exercises of it and drops the rest, and is itself
        dropped once none are left. The session stays, components or not, so a
        filtered program still has all its sessions to show.
        """
        filtered = self.model_copy(deep=True)
        kept: list[WorkoutComponent_t] = []
        for component in filtered.workout_components:
            if isinstance(component, SingleExercise):
                if component.exercise.name in exercise_names:
                    kept.append(component)
                continue
            for exercise in list(component.exercises):
                if exercise.name not in exercise_names:
                    component.remove_exercise(exercise)
            if component.exercises:
                kept.append(component)
        filtered.workout_components = kept
        return filtered


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
