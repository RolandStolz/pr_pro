"""Pieces the visualization modules share."""

from __future__ import annotations

from pr_pro.program import Program

UNPHASED: str = 'Unphased'


def phase_of_session(program: Program) -> dict[str, str]:
    """The phase each session belongs to; program_phases holds the reverse."""
    return {
        session_id: phase
        for phase, session_ids in program.program_phases.items()
        for session_id in session_ids
    }


def phase_order(program: Program) -> list[str]:
    """The program's phases, with a trailing group for sessions outside them."""
    order = list(program.program_phases)
    if len(phase_of_session(program)) < len(program.workout_session_dict):
        order.append(UNPHASED)
    return order
