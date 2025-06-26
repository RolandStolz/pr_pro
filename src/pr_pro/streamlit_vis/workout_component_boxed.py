import streamlit as st

from pr_pro.streamlit_vis.sets import display_set_details_ui
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
        for set_idx, working_set in enumerate(component.sets):
            checkbox_key = f'{session.id}_{component.exercise.name}_{set_idx}'
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False

            if use_persistent_state:
                register_key_for_persistence(checkbox_key, default_value=False)

            with st.expander(
                f'**Set {set_idx + 1}**',
                expanded=not st.session_state[checkbox_key],
                icon='✅' if st.session_state[checkbox_key] else None,
            ):
                cols = st.columns([1, 7], border=False, vertical_alignment='top')
                with cols[0]:
                    # st.markdown(f'**Set {set_idx + 1}**')
                    st.checkbox(
                        'done',
                        key=f'{session.id}_{component.exercise.name}_{set_idx}',
                        on_change=save_persisted_state_to_file if use_persistent_state else None,
                    )
                with cols[1]:
                    display_set_details_ui(working_set)
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

        for set_idx in range(num_sets):
            checkbox_key = f'{session.id}_{"_".join(e.name for e in component.exercises)}_{set_idx}'
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False

            if use_persistent_state:
                register_key_for_persistence(checkbox_key, default_value=False)

            with st.expander(
                f'**Set {set_idx + 1}**',
                expanded=not st.session_state[checkbox_key],
                icon='✅' if st.session_state[checkbox_key] else None,
            ):
                cols = st.columns(
                    [1] + [7 / num_exercises_in_group] * num_exercises_in_group,
                    border=False,
                    vertical_alignment='top',
                )
                with cols[0]:
                    st.checkbox(
                        'done',
                        key=f'{session.id}_{"_".join(e.name for e in component.exercises)}_{set_idx}',
                        on_change=save_persisted_state_to_file if use_persistent_state else None,
                    )
                for i, exercise_in_group in enumerate(component.exercises):
                    cols[i + 1].markdown(f'**{exercise_in_group.name}**')
                    with cols[i + 1]:
                        if set_idx < len(component.exercise_sets_dict[exercise_in_group]):
                            working_set = component.exercise_sets_dict[exercise_in_group][set_idx]
                            display_set_details_ui(working_set)
                        else:
                            st.caption('N/A')
    else:
        st.info('No sets or exercises defined for this group, or sets are empty.')
