from __future__ import annotations

from collections.abc import Collection, Iterable
from inspect import cleandoc
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator

from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise, Exercise_t
from pr_pro.workout_session import WorkoutSession


class Program(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str
    description: str | None = None
    best_exercise_values: dict[Exercise_t, float] = {}
    workout_session_dict: dict[str, WorkoutSession] = {}
    program_phases: dict[str, list[str]] = {}

    @field_validator('description')
    @classmethod
    def _clean_description(cls, v: str | None) -> str | None:
        """Strip the source indentation a triple-quoted description carries."""
        return cleandoc(v) if v else v

    def __str__(self) -> str:
        workout_str = f'--- Workout {self.name} ---\n'
        description_str = f'{self.description}\n\n' if self.description else ''
        best_exercise_str = (
            'Best exercise values\n  '
            + '\n  '.join([f'{e.name}: {value}' for e, value in self.best_exercise_values.items()])
            + '\n\n'
        )
        workout_sessions_str = (
            'Workout sessions\n'
            + '\n'.join(ws.__str__() for ws in self.workout_session_dict.values())
            + '\n'
        )
        return workout_str + description_str + best_exercise_str + workout_sessions_str

    def add_workout_session(self, workout_session: WorkoutSession) -> Self:
        if workout_session.id in self.workout_session_dict:
            raise ValueError(
                f'Workout session with id {workout_session.id} already exists in the program.'
            )
        self.workout_session_dict[workout_session.id] = workout_session
        return self

    def add_program_phase(self, phase_id: str, session_ids: list[str]) -> Self:
        if phase_id in self.program_phases:
            raise ValueError(f'Program phase with id {phase_id} already exists.')
        if not all(session_id in self.workout_session_dict for session_id in session_ids):
            raise ValueError('One or more session IDs do not exist in the program.')
        self.program_phases[phase_id] = session_ids
        return self

    def get_workout_session_by_id(self, session_id: str) -> WorkoutSession | None:
        return self.workout_session_dict.get(session_id, None)

    def get_exercise_names(self) -> list[str]:
        """Every exercise the program trains, in the order its sessions introduce them."""
        return list(
            dict.fromkeys(
                name
                for session in self.workout_session_dict.values()
                for name in session.get_exercise_names()
            )
        )

    def filter_exercises(self, exercise_names: Collection[str]) -> Program:
        """A copy of the program holding only the named exercises.

        Every session, phase and best value stays, so the copy drops into anything
        that takes a program: the plots and tables then describe those exercises
        alone, over the shape of the whole program.
        """
        unknown = sorted(set(exercise_names) - set(self.get_exercise_names()))
        if unknown:
            raise ValueError(f'Program {self.name} trains no exercise {unknown}.')

        filtered = self.model_copy(deep=True)
        filtered.workout_session_dict = {
            session_id: session.filter_exercises(exercise_names)
            for session_id, session in self.workout_session_dict.items()
        }
        return filtered

    def add_best_exercise_value(self, exercise: Exercise_t, value: float) -> Self:
        self.best_exercise_values[exercise] = value
        return self

    def compute_values(self, compute_config: ComputeConfig) -> None:
        for session in self.workout_session_dict.values():
            session.compute_values(self.best_exercise_values, compute_config)

    @field_serializer('best_exercise_values')
    def serialize_best_exercise_values(self, v: dict[Exercise, float], _info) -> dict[str, float]:
        return {key.__str__(): value for key, value in v.items()}

    def write_json_file(self, file_path: Path) -> None:
        with open(file_path, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    def export_to_pdf(
        self,
        file_path: Path | None = None,
        exclude_metrics: Iterable[str] = (),
        notes_field: bool = False,
    ) -> bytes:
        """Render the program to a PDF and return it as bytes.

        file_path, when given, also writes the PDF to that file.

        exclude_metrics names set fields to leave out of the tables, for example
        ('relative_percentage', 'percentage').

        notes_field adds an empty, fillable text box at the end of each session page
        that the reader can type into and save from a PDF viewer.
        """
        try:
            from pr_pro.pdf_export import export_program_to_pdf
        except ImportError as e:
            raise ImportError(
                "PDF export requires additional dependencies. Please install with 'pip install pr_pro[vis]'"
            ) from e
        return export_program_to_pdf(
            self, file_path, exclude_metrics=exclude_metrics, notes_field=notes_field
        )

    @staticmethod
    def from_json_file(file_path: Path) -> Program:
        with open(file_path, 'r') as f:
            return Program.model_validate_json(f.read())
