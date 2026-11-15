import pytest

from pr_pro.exercises.common import backsquat
from pr_pro.visualization.visualize_sessions import (
    build_session_table,
    print_session_table,
    sets_text,
)
from pr_pro.workout_component import SingleExercise
from pr_pro.workout_session import WorkoutSession


def test_identical_sets_collapse_into_a_run():
    sets = [backsquat.create_set(5, weight=100) for _ in range(4)]

    assert sets_text(sets) == '4x5 @ 100kg'


def test_a_ramp_collapses_to_the_span_it_covers():
    """Same reps throughout, so six singles are one entry, not six."""
    sets = [backsquat.create_set(1, weight=w) for w in (60, 65, 70, 75, 80, 85)]

    assert sets_text(sets) == '6x1 @ 60-85kg'


def test_a_change_of_reps_starts_a_new_entry():
    sets = [backsquat.create_set(5, weight=100)] * 2 + [backsquat.create_set(3, weight=120)] * 2

    assert sets_text(sets) == '2x5 @ 100kg, 2x3 @ 120kg'


def test_kilos_and_percentages_do_not_share_an_entry():
    sets = [
        backsquat.create_set(5, weight=100),
        backsquat.create_set(5, percentage=0.8),
    ]

    assert sets_text(sets) == '5 @ 100kg, 5 @ 80%'


def test_differing_sets_are_listed_in_order():
    sets = [
        backsquat.create_set(5, weight=100),
        backsquat.create_set(5, weight=100),
        backsquat.create_set(3, weight=120),
    ]

    assert sets_text(sets) == '2x5 @ 100kg, 3 @ 120kg'


def test_table_has_a_column_per_session_and_blanks_elsewhere(example_program):
    table = build_session_table(example_program, ['W1D1', 'W1D2'])

    assert list(table.columns) == ['W1D1', 'W1D2']
    # Every exercise is trained by at least one of the two, none by necessity by both.
    assert (table != '').any(axis=1).all()
    assert (table == '').to_numpy().any()


def test_table_covers_every_session_by_default(example_program):
    table = build_session_table(example_program)

    assert list(table.columns) == list(example_program.workout_session_dict)


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


def test_table_rows_follow_the_order_sessions_introduce_them(session_a, basic_program):
    session_a.add_component(
        SingleExercise(exercise=backsquat).add_repeating_set(2, backsquat.create_set(5, weight=60))
    )
    later = WorkoutSession(id='later').add_component(
        SingleExercise(exercise=backsquat).add_repeating_set(1, backsquat.create_set(3, weight=80))
    )
    basic_program.add_workout_session(session_a).add_workout_session(later)

    table = build_session_table(basic_program)

    assert list(table.index) == [backsquat.name]
    assert table.loc[backsquat.name, 'later'] == '3 @ 80kg'


def test_transposed_print_runs_sessions_down_the_page(example_program, capsys):
    print_session_table(example_program, exercises=['Backsquat'], transpose=True)

    printed = capsys.readouterr().out
    header, first_row = printed.splitlines()[:2]
    assert header.split() == ['exercise', 'Backsquat']
    assert first_row.startswith('W1D1')
