from typing import Any, Callable, Optional, List, Tuple

import pandas as pd
from pr_pro.sets import (
    WorkingSet_t,
    RepsSet,
    RepsRPESet,
    RepsAndWeightsSet,
    PowerExerciseSet,
    DurationSet,
)
import streamlit as st


MetricConfig = Tuple[str, str, Optional[Callable[[Any], Any]]]


def _build_metrics_list(ws: WorkingSet_t, configs: List[MetricConfig]) -> List[Tuple[str, Any]]:
    """
    Builds a list of metrics from a working set based on configurations.

    Args:
        ws: The working set object.
        configs: A list of tuples, where each tuple contains:
                 (attribute_name, display_label, optional_formatter_function)
    """
    metrics = []
    for attr_name, label, formatter in configs:
        if hasattr(ws, attr_name):
            value = getattr(ws, attr_name)
            if value is not None:  # Ensure attribute has a meaningful value
                display_value = formatter(value) if formatter else value
                metrics.append((label, display_value))
    return metrics


def _render_rest_caption(ws: WorkingSet_t) -> None:
    """Renders the rest duration caption if available."""
    if hasattr(ws, 'rest_between') and ws.rest_between:
        st.caption(f'Rest: {ws.rest_between}')


def render_set_metrics_df_style(metrics: list[tuple[str, Any]]) -> None:
    # Note: The dataframe display would probably look nice, when all sets are displayed in one
    st.markdown(
        """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
        unsafe_allow_html=True,
    )
    """Helper to render a list of metrics in dynamically sized columns."""
    valid_metrics = [m for m in metrics if m[1] is not None]
    if not valid_metrics:
        st.caption('No specific details available.')
        return

    # Create a DataFrame with labels as the index
    df = pd.DataFrame.from_records(valid_metrics, columns=['Metric', 'Value']).set_index('Metric')

    # Transpose the DataFrame so metrics become columns
    df_transposed = df.transpose()

    st.dataframe(df_transposed, hide_index=True, use_container_width=True)


def render_set_metrics(metrics: list[tuple[str, Any]]) -> None:
    """Helper to render a list of metrics in dynamically sized columns."""
    valid_metrics = [m for m in metrics if m[1] is not None]
    if not valid_metrics:
        st.caption('No specific details.')
        return

    num_columns = len(valid_metrics)
    cols = st.columns(num_columns)
    col_idx = 0
    for label, value in valid_metrics:
        display_value = value

        # Ensure display_value is a type st.metric can handle directly, or convert to string
        if not isinstance(value, (int, float, complex, str)):
            display_value = str(value)

        cols[col_idx].metric(label, display_value)
        col_idx += 1


def render_reps_set_details(ws: RepsSet):
    configs: List[MetricConfig] = [
        ('reps', 'Reps', None),
    ]
    metrics = _build_metrics_list(ws, configs)
    render_set_metrics(metrics)
    _render_rest_caption(ws)


def render_reps_rpe_set_details(ws: RepsRPESet):
    configs: List[MetricConfig] = [
        ('reps', 'Reps', None),
        ('rpe', 'RPE', None),
    ]
    metrics = _build_metrics_list(ws, configs)
    render_set_metrics(metrics)
    _render_rest_caption(ws)


def render_reps_and_weights_set_details(ws: RepsAndWeightsSet):
    configs: List[MetricConfig] = [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
        ('relative_percentage', 'Rel %', lambda rp: f'{rp * 100:.0f}%'),
    ]
    metrics = _build_metrics_list(ws, configs)
    render_set_metrics(metrics)
    _render_rest_caption(ws)


def render_power_exercise_set_details(ws: PowerExerciseSet):
    configs: List[MetricConfig] = [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
    ]
    metrics = _build_metrics_list(ws, configs)
    render_set_metrics(metrics)
    _render_rest_caption(ws)


def render_duration_set_details(ws: DurationSet):
    configs: List[MetricConfig] = [
        (
            'duration',
            'Duration',
            lambda d: d.strftime('%M:%S') if hasattr(d, 'strftime') else str(d),
        ),
    ]
    metrics = _build_metrics_list(ws, configs)
    render_set_metrics(metrics)
    _render_rest_caption(ws)


def render_unknown_set_details(ws: WorkingSet_t):
    st.markdown(f'`{str(ws)}`')


def display_set_details_ui(working_set: WorkingSet_t):
    """Dispatches to a specific rendering function based on set type."""
    # Important: Order of isinstance checks matters if classes have inheritance.
    # More specific derived classes should be checked before their base classes.
    if isinstance(working_set, RepsAndWeightsSet):
        render_reps_and_weights_set_details(working_set)
    elif isinstance(working_set, RepsRPESet):
        render_reps_rpe_set_details(working_set)
    elif isinstance(working_set, PowerExerciseSet):
        render_power_exercise_set_details(working_set)
    elif isinstance(working_set, RepsSet):
        render_reps_set_details(working_set)
    elif isinstance(working_set, DurationSet):
        render_duration_set_details(working_set)
    else:
        render_unknown_set_details(working_set)
