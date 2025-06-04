import streamlit as st

from pr_pro.configs import ComputeConfig
from pr_pro.example import get_example_program
from pr_pro.program import Program
from pr_pro.streamlit_vis.session import render_session


def run_streamlit_app(program: Program):
    st.set_page_config(layout='wide', page_title='PR-Pro Visualizer')

    st.title(program.name)

    # Sidebar
    with st.sidebar:
        st.markdown('Source: [rolandstolz/pr_pro](https://github.com/rolandstolz/pr_pro)')

        if program.best_exercise_values:
            st.title('Max values')
            for exercise, value in program.best_exercise_values.items():
                st.markdown(f'**{exercise.name}**: {value:.1f} kg')

    # Sessions
    session_ids = [session.id for session in program.workout_sessions]
    if not session_ids:
        st.error('Program has no workout sessions.')
        st.stop()

    selected_session_id = st.selectbox('Select Workout Session', options=session_ids, index=0)
    selected_session = next(
        (s for s in program.workout_sessions if s.id == selected_session_id), None
    )

    if selected_session:
        render_session(selected_session)
    else:
        st.error('Selected session not found.')

    st.divider()
    with st.expander('Session comparison'):
        sessino_ids_remaining = [
            session_id for session_id in session_ids if session_id != selected_session_id
        ]
        selected_session_comparison_id = st.selectbox(
            'Select Workout Session', options=sessino_ids_remaining, index=0
        )
        selected_session_comparison = next(
            (s for s in program.workout_sessions if s.id == selected_session_comparison_id), None
        )
        if selected_session_comparison:
            render_session(selected_session_comparison)


if __name__ == '__main__':
    program = get_example_program()
    program.compute_values(compute_config=ComputeConfig())
    run_streamlit_app(program)
