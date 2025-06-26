import streamlit as st

from pr_pro.configs import ComputeConfig
from pr_pro.example import get_example_program
from pr_pro.program import Program
from pr_pro.streamlit_vis.session import render_session
from pr_pro.streamlit_vis.state import load_persisted_state_from_file

st.set_page_config(layout='wide', page_title='PR-Pro Visualizer')


def run_streamlit_app(program: Program, use_persistent_state: bool = False):
    if use_persistent_state:
        load_persisted_state_from_file()

    st.title(program.name)

    # Sidebar
    with st.sidebar:
        st.markdown('Source: [rolandstolz/pr_pro](https://github.com/rolandstolz/pr_pro)')

        if program.best_exercise_values:
            st.title('Max values')
            for exercise, value in program.best_exercise_values.items():
                st.markdown(f'**{exercise.name}**: {round(value, 1)} kg')

    # Sessions
    if not program.program_phases:
        session_ids = list(program.workout_session_dict.keys())
    else:
        phase = st.pills(
            'Phases', program.program_phases.keys(), default=list(program.program_phases.keys())[0]
        )
        session_ids = program.program_phases[phase]  # type: ignore
    if not session_ids:
        st.error('No workout sesssions.')
        st.stop()

    selected_session_id = st.pills('Select Workout Session', session_ids, default=session_ids[0])
    selected_session = program.get_workout_session_by_id(selected_session_id)  # type: ignore

    if selected_session:
        render_session(selected_session, use_persistent_state=use_persistent_state)
    else:
        st.error('Selected session not found.')

    st.divider()

    st.checkbox('Show session comparison', value=False, key='show_comparison')
    if st.session_state.get('show_comparison', False):
        phase = st.pills(
            'Phases',
            program.program_phases.keys(),
            default=list(program.program_phases.keys())[0],
            key='comparison_phase',
        )
        session_ids_remaining = [
            sid
            for sid in program.program_phases[phase]  # type: ignore
            if sid != selected_session_id
        ]
        selected_session_comparison_id = st.selectbox(
            'Select Workout Session', options=session_ids_remaining, index=0
        )
        selected_session_comparison = program.get_workout_session_by_id(
            selected_session_comparison_id
        )
        if selected_session_comparison:
            render_session(selected_session_comparison, use_persistent_state)


@st.cache_data
def load_program_data():
    program = get_example_program()
    program.compute_values(compute_config=ComputeConfig())
    return program


if __name__ == '__main__':
    program = load_program_data()
    run_streamlit_app(program, use_persistent_state=False)
