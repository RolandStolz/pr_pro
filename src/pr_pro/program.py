from __future__ import annotations
from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_serializer

from pr_pro.workout_session import WorkoutSession
from pr_pro.configs import ComputeConfig
from pr_pro.exercise import Exercise, Exercise_t


class Program(BaseModel):
    name: str
    best_exercise_values: dict[Exercise_t, float] = {}
    workout_session_dict: dict[str, WorkoutSession] = {}
    program_phases: dict[str, list[str]] = {}

    def __str__(self) -> str:
        workout_str = f'--- Workout {self.name} ---\n'
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
        return workout_str + best_exercise_str + workout_sessions_str

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

    def export_to_pdf(self, file_path: Path) -> None:
        try:
            from pr_pro.pdf_export import export_program_to_pdf
        except ImportError as e:
            raise ImportError(
                "PDF export requires additional dependencies. Please install with 'pip install pr_pro[vis]'"
            ) from e
        export_program_to_pdf(self, file_path)

    @staticmethod
    def from_json_file(file_path: Path) -> Program:
        with open(file_path, 'r') as f:
            return Program.model_validate_json(f.read())
