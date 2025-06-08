from __future__ import annotations
from abc import abstractmethod
from copy import deepcopy
import logging
from typing import Any, Self, Sequence

from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator

from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise_t, RepsAndWeightsExercise
from pr_pro.sets import WorkingSet_t

logger = logging.getLogger(__name__)


class WorkoutComponent(BaseModel):
    notes: str | None = None
    model_config = ConfigDict(validate_assignment=True)

    @staticmethod
    @abstractmethod
    def from_prev_component(component: WorkoutComponent, **kwargs) -> WorkoutComponent: ...

    @abstractmethod
    def add_set(self, working_set: WorkingSet_t) -> Self: ...

    def set_notes(self, notes: str) -> Self:
        self.notes = notes
        return self

    def add_repeating_set(self, n_repeats: int, working_set: WorkingSet_t) -> Self:
        for _ in range(n_repeats):
            self.add_set(working_set.model_copy())
        return self

    def add_rs(self, n_repeats: int, working_set: WorkingSet_t) -> Self:
        return self.add_repeating_set(n_repeats, working_set)

    @abstractmethod
    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None: ...


class SingleExercise(WorkoutComponent):
    exercise: Exercise_t
    sets: list[WorkingSet_t] = []

    @model_validator(mode='after')
    def check_same_type(self, info: ValidationInfo) -> Self:
        if not all(isinstance(s, self.exercise.set_class) for s in self.sets):
            raise ValueError(f'All sets must be of type {self.exercise.set_class.__name__}.')
        return self

    @staticmethod
    def from_prev_component(component: SingleExercise, **kwargs) -> SingleExercise:
        new_component = component.model_copy(deep=True)
        if 'sets' in kwargs:
            n_sets = len(component.sets)
            assert n_sets > 0
            new_component.sets = []
            new_component.add_repeating_set(kwargs['sets'] + n_sets, component.sets[0])
            del kwargs['sets']

        for key, value in kwargs.items():
            for w_set in new_component.sets:
                w_set.__setattr__(key, w_set.__getattribute__(key) + value)

        return new_component

    def __str__(self) -> str:
        line_start = '\n  '
        notes_str = f'{line_start}notes: {self.notes}' if self.notes else ''
        return (
            str(self.exercise.name)
            + f' with {len(self.sets)} sets:'
            + notes_str
            + line_start
            + line_start.join(s.__str__() for s in self.sets)
        )

    def add_set(self, working_set: WorkingSet_t) -> Self:
        self.sets.append(working_set)
        return self

    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None:
        best_value = best_exercise_values.get(self.exercise)

        # If not found, try to find an associated exercise and get its value.
        if best_value is None:
            associated_exercise = compute_config.exercise_associations.get(self.exercise)
            if not associated_exercise:
                return None
            best_value = best_exercise_values.get(associated_exercise)

        if best_value is None:
            return None

        for working_set in self.sets:
            working_set.compute_values(best_value, compute_config)


class ExerciseGroup(WorkoutComponent):
    exercises: list[Exercise_t]
    exercise_sets_dict: dict[Exercise_t, list[WorkingSet_t]] = {}

    def model_post_init(self, context: Any) -> None:
        if len(self.exercises) != len(set(self.exercises)):
            raise ValueError('Exercises must be unique in the group.')

        if len(self.exercises) > 0:
            # Only create the empty lists, if the exercise key's don't exist yet (e.g., after model validation)
            if self.exercises[0] not in self.exercise_sets_dict:
                self.exercise_sets_dict = {e: [] for e in self.exercises}

    @staticmethod
    def from_prev_component(component: ExerciseGroup, **kwargs) -> ExerciseGroup:
        new_component = component.model_copy(deep=True)

        if 'sets' in kwargs:
            n_sets = len(component.exercise_sets_dict[component.exercises[0]])
            assert n_sets > 0
            for e in component.exercises:
                new_component.exercise_sets_dict[e] = [
                    component.exercise_sets_dict[e][0].model_copy(deep=True)
                    for _ in range(kwargs['sets'] + n_sets)
                ]
            del kwargs['sets']

        for key, value in kwargs.items():
            assert isinstance(value, Sequence)
            assert len(value) == len(component.exercises)

            for i, e in enumerate(component.exercises):
                if value[i] is not None:
                    for w_set in new_component.exercise_sets_dict[e]:
                        w_set.__setattr__(key, w_set.__getattribute__(key) + value[i])

        return new_component

    @model_validator(mode='after')
    def check_same_type(self, info: ValidationInfo) -> Self:
        for exercise, sets in self.exercise_sets_dict.items():
            if not all(isinstance(s, exercise.set_class) for s in sets):
                raise ValueError(
                    f'All sets for {exercise.name} must be of type {exercise.set_class.__name__}.'
                )
        return self

    def add_exercise(self, exercise: Exercise_t) -> Self:
        if exercise in self.exercises:
            raise ValueError(f'Exercise {exercise.name} is already part of this group.')
        self.exercises.append(exercise)
        self.exercise_sets_dict[exercise] = []
        return self

    def remove_exercise(self, exercise: Exercise_t) -> Self:
        if exercise not in self.exercises:
            raise ValueError(f'Exercise {exercise.name} is not part of this group.')

        self.exercises.remove(exercise)
        del self.exercise_sets_dict[exercise]
        return self

    def add_set(self, working_set: WorkingSet_t, *, exercise: Exercise_t) -> Self:
        if exercise not in self.exercises:
            raise ValueError(f'Exercise {exercise.name} is not part of this group.')

        self.exercise_sets_dict[exercise].append(working_set)
        return self

    def add_repeating_set(
        self, n_repeats: int, working_set: WorkingSet_t, *, exercise: Exercise_t
    ) -> Self:
        for _ in range(n_repeats):
            self.add_set(working_set.model_copy(), exercise=exercise)
        return self

    def __str__(self) -> str:
        line_start = '\n  '
        notes_str = f'{line_start}notes: {self.notes}' if self.notes else ''
        n_sets = len(self.exercise_sets_dict[self.exercises[0]])
        return (
            ' + '.join(e.name for e in self.exercises)
            + f' with {n_sets} sets:'
            + notes_str
            + line_start
            + line_start.join(
                ' | '.join(self.exercise_sets_dict[e][i].__str__() for e in self.exercises)
                for i in range(n_sets)
            )
        )

    def add_group_sets(self, exercise_sets: dict[Exercise_t, WorkingSet_t]) -> Self:
        if len(exercise_sets) != len(self.exercises):
            raise ValueError(
                f'Expected {len(self.exercises)} sets (one for each exercise), got {len(exercise_sets)}.'
            )

        for exercise, working_set in exercise_sets.items():
            if exercise not in self.exercises:
                raise ValueError(f'Exercise {exercise.name} is not part of this group.')

            self.exercise_sets_dict[exercise].append(working_set)
        return self

    def add_gs(self, exercise_sets: dict[Exercise_t, WorkingSet_t]) -> Self:
        return self.add_group_sets(exercise_sets)

    def add_repeating_group_sets(
        self, n_repeats: int, exercise_sets: dict[Exercise_t, WorkingSet_t]
    ) -> Self:
        for _ in range(n_repeats):
            self.add_group_sets(deepcopy(exercise_sets))
        return self

    def add_rgs(self, n_repeats: int, exercise_sets: dict[Exercise_t, WorkingSet_t]) -> Self:
        return self.add_repeating_group_sets(n_repeats, exercise_sets)

    def compute_values(
        self, best_exercise_values: dict[Exercise_t, float], compute_config: ComputeConfig
    ) -> None:
        for exercise, sets in self.exercise_sets_dict.items():
            best_value = best_exercise_values.get(exercise)

            # If not found, try to find an associated exercise and get its value.
            if best_value is None:
                associated_exercise = compute_config.exercise_associations.get(exercise)
                if not associated_exercise:
                    return None
                best_value = best_exercise_values.get(associated_exercise)

            if best_value is None:
                return None

            for working_set in sets:
                working_set.compute_values(best_value, compute_config)


WorkoutComponent_t = SingleExercise | ExerciseGroup


if __name__ == '__main__':  # pragma: no cover
    bench_press = RepsAndWeightsExercise(name='Benchpress')
    row = RepsAndWeightsExercise(name='Row')
    squat = RepsAndWeightsExercise(name='Squat')

    co = SingleExercise(exercise=squat)
    co.add_repeating_set(3, squat.create_set(10, 80))

    co2 = SingleExercise.from_prev_component(co, sets=+1, reps=-2, weight=+10)
    print(co)
    print(co2)
    print()

    gco = ExerciseGroup(exercises=[bench_press, row]).add_repeating_group_sets(
        4,
        {
            bench_press: bench_press.create_set(10, 60),
            row: row.create_set(10, 60),
        },
    )

    gco2 = ExerciseGroup.from_prev_component(gco, reps=(+2, +2))
    print(gco)
    print(gco2)
