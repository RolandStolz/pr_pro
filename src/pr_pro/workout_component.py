from __future__ import annotations
from abc import abstractmethod
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator

from pr_pro.exercise import Exercise, RepsAndWeightsExercise
from pr_pro.sets import WorkingSet


class WorkoutComponent(BaseModel):
    notes: str | None = None
    model_config = ConfigDict(validate_assignment=True)

    @staticmethod
    @abstractmethod
    def from_prev_component(component: WorkoutComponent, **kwargs) -> WorkoutComponent: ...

    @abstractmethod
    def add_set(self, working_set: WorkingSet) -> Self: ...

    def add_repeating_set(self, n_repeats: int, working_set: WorkingSet) -> Self:
        for _ in range(n_repeats):
            self.add_set(working_set)
        return self

    def add_rs(self, n_repeats: int, working_set: WorkingSet) -> Self:
        return self.add_repeating_set(n_repeats, working_set)


class SingleExercise(WorkoutComponent):
    exercise: Exercise
    sets: list[WorkingSet] = []

    @model_validator(mode='after')
    def check_same_type(self, info: ValidationInfo) -> Self:
        if not all(isinstance(s, self.exercise.set_class) for s in self.sets):
            raise ValueError(f'All sets must be of type {self.exercise.set_class.__name__}.')
        return self

    @staticmethod
    def from_prev_component(component: SingleExercise, **kwargs) -> SingleExercise:
        new_component = component.model_copy()
        if kwargs['sets']:
            n_sets = len(component.sets)
            assert n_sets > 0
            new_component.sets = [component.sets[0]] * (kwargs['sets'] + n_sets)

        del kwargs['sets']

        for key, value in kwargs.items():
            # for w_set in new_component.sets:
            w_set = new_component.sets[0]
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

    def add_set(self, working_set: WorkingSet) -> Self:
        self.sets.append(working_set)
        return self


class ExerciseGroup(WorkoutComponent):
    exercises: list[Exercise]
    exercise_sets_dict: dict[Exercise, list[WorkingSet]] = {}

    def model_post_init(self, context: Any) -> None:
        if len(self.exercises) != len(set(self.exercises)):
            raise ValueError('Exercises must be unique in the group.')

        self.exercise_sets_dict = {e: [] for e in self.exercises}

    @staticmethod
    def from_prev_component(component: ExerciseGroup, **kwargs) -> ExerciseGroup:
        raise NotImplementedError

    @model_validator(mode='after')
    def check_same_type(self, info: ValidationInfo) -> Self:
        for exercise, sets in self.exercise_sets_dict.items():
            if not all(isinstance(s, exercise.set_class) for s in sets):
                raise ValueError(
                    f'All sets for {exercise.name} must be of type {exercise.set_class.__name__}.'
                )
        return self

    def add_set(self, working_set: WorkingSet, *, exercise: Exercise) -> Self:
        if exercise not in self.exercises:
            raise ValueError(f'Exercise {exercise.name} is not part of this group.')

        self.exercise_sets_dict[exercise].append(working_set)
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
                ' + '.join(self.exercise_sets_dict[e][i].__str__() for e in self.exercises)
                for i in range(n_sets)
            )
        )

    def add_group_sets(self, exercise_sets: dict[Exercise, WorkingSet]) -> Self:
        if len(exercise_sets) != len(self.exercises):
            raise ValueError(
                f'Expected {len(self.exercises)} sets (one for each exercise), got {len(exercise_sets)}.'
            )

        for exercise, working_set in exercise_sets.items():
            if exercise not in self.exercises:
                raise ValueError(f'Exercise {exercise.name} is not part of this group.')

            self.exercise_sets_dict[exercise].append(working_set)
        return self

    def add_gs(self, exercise_sets: dict[Exercise, WorkingSet]) -> Self:
        return self.add_group_sets(exercise_sets)

    def add_repeating_group_sets(
        self, n_repeats: int, exercise_sets: dict[Exercise, WorkingSet]
    ) -> Self:
        for _ in range(n_repeats):
            self.add_group_sets(exercise_sets)
        return self

    def add_rgs(self, n_repeats: int, exercise_sets: dict[Exercise, WorkingSet]) -> Self:
        return self.add_repeating_group_sets(n_repeats, exercise_sets)


if __name__ == '__main__':
    bench_press = RepsAndWeightsExercise(name='Benchpress')
    row = RepsAndWeightsExercise(name='Row')
    squat = RepsAndWeightsExercise(name='Squat')

    component = SingleExercise(exercise=squat)
    component.add_repeating_set(3, squat.create_set(10, 80))

    component2 = SingleExercise.from_prev_component(component, sets=+1, reps=-2, weight=+10, a=+1)
    print(component2)
