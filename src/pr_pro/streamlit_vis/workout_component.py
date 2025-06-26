import streamlit as st

from pr_pro.streamlit_vis.sets import display_sets_table_ui
from pr_pro.streamlit_vis.state import register_key_for_persistence, save_persisted_state_to_file
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession


def _add_comment(component_key: str, use_persistent_state: bool):
    if use_persistent_state:
        register_key_for_persistence(component_key, default_value='')

    st.text_input(
        'Comment',
        key=component_key,
        on_change=save_persisted_state_to_file if use_persistent_state else None,
    )


def render_single_exercise_component_ui(
    component: SingleExercise, session: WorkoutSession, use_persistent_state: bool
):
    if component.notes:
        st.markdown(f'**Notes**: *{component.notes}*')

    component_key = f'{session.id}_{component.exercise.name}_comment'
    _add_comment(component_key, use_persistent_state)

    if component.sets:
        display_sets_table_ui(component.sets)
    else:
        st.info('No sets defined for this exercise.')


def render_exercise_group_component_ui(
    component: ExerciseGroup, session: WorkoutSession, use_persistent_state: bool
):
    if component.notes:
        st.caption(f'**Notes**: *{component.notes}*')

    component_key = f'{session.id}_{"_".join(e.name for e in component.exercises)}_comment'
    _add_comment(component_key, use_persistent_state)

    if (
        component.exercise_sets_dict
        and component.exercises
        and component.exercise_sets_dict.get(component.exercises[0])
    ):
        num_sets = len(component.exercise_sets_dict[component.exercises[0]])
        num_exercises_in_group = len(component.exercises)

        if num_sets == 0:
            st.info('No sets defined for this exercise group.')
            return

        cols = st.columns(
            num_exercises_in_group,
            border=False,
            vertical_alignment='top',
        )

        for i, exercise_in_group in enumerate(component.exercises):
            with cols[i]:
                st.markdown(f'**{exercise_in_group.name}**')
                sets = component.exercise_sets_dict[exercise_in_group]
                if sets:
                    display_sets_table_ui(sets)
                else:
                    st.info('No sets defined for this exercise.')

    else:
        st.info('No sets or exercises defined for this group, or sets are empty.')
