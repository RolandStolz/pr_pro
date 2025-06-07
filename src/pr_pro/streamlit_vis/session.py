from pr_pro.streamlit_vis.workout_component import (
    render_exercise_group_component_ui,
    render_single_exercise_component_ui,
)
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession
import streamlit as st


def render_session(session: WorkoutSession, use_persistent_state: bool):
    st.subheader(f'Session: {session.id}')
    if session.notes:
        st.markdown(f'> _{session.notes}_')

    with st.expander('Session stats'):
        st.markdown(f'Exercises: {session.get_number_of_exercises()}')
        st.markdown(f'Sets: {session.get_number_of_sets()}')

    component_tab_titles = []
    for comp in session.workout_components:
        if isinstance(comp, SingleExercise):  #
            component_tab_titles.append(f'{comp.exercise.name}')
        elif isinstance(comp, ExerciseGroup):  #
            group_name = ' + '.join([ex.name for ex in comp.exercises])
            component_tab_titles.append(f'{group_name}')
        else:
            component_tab_titles.append('Unknown Component')

    if component_tab_titles:
        tabs = st.tabs(component_tab_titles)
        for i, component in enumerate(session.workout_components):
            with tabs[i]:
                if isinstance(component, SingleExercise):  #
                    render_single_exercise_component_ui(
                        component, session=session, use_persistent_state=use_persistent_state
                    )
                elif isinstance(component, ExerciseGroup):  #
                    render_exercise_group_component_ui(
                        component, session=session, use_persistent_state=use_persistent_state
                    )
                else:
                    st.warning(f'Unknown component type: {type(component)}')
    else:
        st.info('This session has no workout components.')
