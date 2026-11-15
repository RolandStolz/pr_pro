import datetime

import pytest

from pr_pro.exercise import DurationExercise
from pr_pro.exercises.common import backsquat, deadlift
from pr_pro.visualization.visualize_sessions import (
    build_session_table,
    print_session_table,
    sets_text,
)
from pr_pro.workout_component import SingleExercise
from pr_pro.workout_session import WorkoutSession


def test_sets_of_the_same_reps_collapse_whatever_they_are_loaded_with():
    """A ramp is six singles at six loads, and still just 6x1 here."""
    sets = [backsquat.create_set(1, weight=w) for w in (60, 65, 70, 75, 80, 85)]

    assert sets_text(sets) == '6x1'


def test_a_change_of_reps_starts_a_new_entry():
    """And a lone set carries no count."""
    sets = [backsquat.create_set(5, weight=100)] * 2 + [backsquat.create_set(3, weight=120)]

    assert sets_text(sets) == '2x5, 3'


def test_a_duration_set_shows_its_duration():
    plank = DurationExercise(name='Plank')
    sets = [plank.create_set(datetime.timedelta(seconds=90))] * 3

    assert sets_text(sets) == '3x1:30'


def test_columns_are_the_chosen_sessions_or_all_of_them(example_program):
    assert list(build_session_table(example_program, ['W1D1', 'W1D2']).columns) == ['W1D1', 'W1D2']
    assert list(build_session_table(example_program).columns) == list(
        example_program.workout_session_dict
    )


def test_filter_keeps_the_named_exercises_in_the_order_given(example_program):
    table = build_session_table(example_program, exercises=['Deadlift', 'Backsquat'])

    assert list(table.index) == ['Deadlift', 'Backsquat']


def test_a_filtered_exercise_the_sessions_skip_keeps_an_empty_row(example_program):
    """So the same selection reads the same from week to week."""
    table = build_session_table(example_program, ['W1D1'], ['Backsquat', 'Deadlift'])

    assert table.loc['Backsquat', 'W1D1'] != ''
    assert table.loc['Deadlift', 'W1D1'] == ''


def test_table_rejects_an_exercise_the_program_never_trains(example_program):
    with pytest.raises(ValueError, match='no exercise'):
        build_session_table(example_program, exercises=['Backsquat', 'Zercher carry'])


def test_table_rejects_an_unknown_session(example_program):
    with pytest.raises(ValueError, match='no session'):
        build_session_table(example_program, ['W1D1', 'nope'])


def test_rows_follow_the_order_sessions_introduce_them(session_a, basic_program):
    """And an exercise trained in both sessions keeps one row."""
    session_a.add_component(
        SingleExercise(exercise=backsquat).add_repeating_set(2, backsquat.create_set(5, weight=60))
    )
    later = (
        WorkoutSession(id='later')
        .add_component(
            SingleExercise(exercise=deadlift).add_repeating_set(
                1, deadlift.create_set(3, weight=120)
            )
        )
        .add_component(
            SingleExercise(exercise=backsquat).add_repeating_set(
                1, backsquat.create_set(3, weight=80)
            )
        )
    )
    basic_program.add_workout_session(session_a).add_workout_session(later)

    table = build_session_table(basic_program)

    assert list(table.index) == [backsquat.name, deadlift.name]
    assert table.loc[backsquat.name, 'later'] == '3'


def test_transposed_print_runs_sessions_down_the_page(example_program, capsys):
    print_session_table(example_program, exercises=['Backsquat'], transpose=True)

    printed = capsys.readouterr().out
    header, first_row = printed.splitlines()[:2]
    assert header.split() == ['exercise', 'Backsquat']
    assert first_row.startswith('W1D1')
