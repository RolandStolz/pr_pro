import streamlit as st

from pr_pro.streamlit_vis.sets import display_set_details_ui
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession


def render_single_exercise_component_ui(component: SingleExercise, session: WorkoutSession):  #
    if component.notes:
        st.caption(f'**Notes**: *{component.notes}*')

    if component.sets:
        for set_idx, working_set in enumerate(component.sets):
            # Use st.container with border for each set's details
            with st.container():
                cols = st.columns([1, 7], border=True, vertical_alignment='top')
                with cols[0]:
                    st.markdown(f'**Set {set_idx + 1}**')
                    st.checkbox('done', key=f'{session.id}_{component.exercise.name}_{set_idx}')
                with cols[1]:
                    display_set_details_ui(working_set)
    else:
        st.info('No sets defined for this exercise.')


def render_exercise_group_component_ui(component: ExerciseGroup, session: WorkoutSession):  #
    if component.notes:
        st.caption(f'**Notes**: *{component.notes}*')

    if (
        component.exercise_sets_dict
        and component.exercises
        and component.exercise_sets_dict.get(component.exercises[0])
    ):
        num_sets = len(component.exercise_sets_dict[component.exercises[0]])
        num_exercises_in_group = len(component.exercises)
        cols = st.columns(
            [1] + [7 / num_exercises_in_group] * num_exercises_in_group,
            border=False,
            vertical_alignment='top',
        )
        for i, exercise_in_group in enumerate(component.exercises):
            cols[i + 1].markdown(f'**{exercise_in_group.name}**')

        if num_sets == 0:
            st.info('No sets defined for this exercise group.')
            return

        for set_idx in range(num_sets):
            with st.container(border=False):
                cols = st.columns(
                    [1] + [7 / num_exercises_in_group] * num_exercises_in_group,
                    border=True,
                    vertical_alignment='top',
                )
                with cols[0]:
                    st.markdown(f'**Set {set_idx + 1}**')
                    st.checkbox(
                        'done',
                        key=f'{session.id}_{"_".join(e.name for e in component.exercises)}_{set_idx}',
                    )
                for i, exercise_in_group in enumerate(component.exercises):
                    with cols[i + 1]:
                        if set_idx < len(component.exercise_sets_dict[exercise_in_group]):
                            working_set = component.exercise_sets_dict[exercise_in_group][set_idx]
                            display_set_details_ui(working_set)
                        else:
                            st.caption('N/A')
    else:
        st.info('No sets or exercises defined for this group, or sets are empty.')
