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

METRIC_CONFIGS: dict[type[WorkingSet_t], list[MetricConfig]] = {
    RepsAndWeightsSet: [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
        ('relative_percentage', 'Rel %', lambda rp: f'{rp * 100:.0f}%'),
    ],
    RepsRPESet: [
        ('reps', 'Reps', None),
        ('rpe', 'RPE', None),
    ],
    PowerExerciseSet: [
        ('reps', 'Reps', None),
        ('weight', 'Weight (kg)', lambda w: f'{round(w, 1)}'),
        ('percentage', 'Abs %', lambda p: f'{p * 100:.0f}%'),
    ],
    RepsSet: [
        ('reps', 'Reps', None),
    ],
    DurationSet: [
        (
            'duration',
            'Duration',
            lambda d: d.strftime('%M:%S') if hasattr(d, 'strftime') else str(d),
        ),
    ],
}


def _get_metric_config(set_instance: WorkingSet_t) -> List[MetricConfig]:
    """
    Gets the metric configuration for a given set instance by checking its type.
    The order of checks is important due to class inheritance.
    """
    for set_type, config in METRIC_CONFIGS.items():
        if isinstance(set_instance, set_type):
            return config
    return []


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


# @st.cache_data
def create_sets_dataframe(_sets: List[WorkingSet_t]) -> pd.DataFrame:
    """
    Creates a DataFrame of metrics for a list of working sets of the same type.

    Args:
        sets: A list of working set objects, all expected to be of the same type.

    Returns:
        A pandas DataFrame where each row represents a set and each column a metric.
    """
    if not _sets:
        return pd.DataFrame()

    first_set = _sets[0]
    configs = _get_metric_config(first_set)

    if not configs:
        return pd.DataFrame([str(s) for s in _sets], columns=['Set Details'])

    all_set_metrics = []
    for i, ws in enumerate(_sets):
        metrics_list = _build_metrics_list(ws, configs)
        metrics_dict = {'Set': i + 1}
        # metrics_dict = {label: value for label, value in metrics_list}
        for label, value in metrics_list:
            metrics_dict[label] = value

        all_set_metrics.append(metrics_dict)

    df = pd.DataFrame(all_set_metrics)
    cols = ['Set'] + [col for col in df.columns if col != 'Set']
    df = df[cols]

    if first_set.rest_between is not None:
        rest_times = [getattr(s, 'rest_between', None) for s in _sets]
        df['Rest'] = rest_times

    return df


def _render_rest_caption(ws: WorkingSet_t) -> None:
    """Renders the rest duration caption if available."""
    if hasattr(ws, 'rest_between') and ws.rest_between:
        st.caption(f'Rest: {ws.rest_between}')


def render_set_metrics(metrics: list[tuple[str, Any]]) -> None:
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

    df = pd.DataFrame.from_records(valid_metrics, columns=['Metric', 'Value']).set_index('Metric')
    df_transposed = df.transpose()
    st.dataframe(df_transposed, hide_index=True, use_container_width=True)


def render_set_metrics_old(metrics: list[tuple[str, Any]]) -> None:
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


def render_unknown_set_details(ws: WorkingSet_t):
    st.markdown(f'`{str(ws)}`')


def display_set_details_ui(working_set: WorkingSet_t):
    """
    Renders the details for any given working set by looking up its configuration.
    This function replaces all the previous, separate render_* functions.
    """
    configs = _get_metric_config(working_set)

    # If no configuration is found for the set type, render it as 'unknown'.
    if not configs:
        render_unknown_set_details(working_set)
        return

    metrics = _build_metrics_list(working_set, configs)
    render_set_metrics(metrics)
    _render_rest_caption(working_set)


def display_sets_table_ui(sets: List[WorkingSet_t]):
    """
    Renders a table of metrics for a list of sets using the new DataFrame function.

    Args:
        sets: A list of working sets, expected to be of the same type.
    """
    df = create_sets_dataframe(sets)

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            # For left alignment
            'Set': st.column_config.TextColumn(),
            'Reps': st.column_config.TextColumn(),
        },
    )
