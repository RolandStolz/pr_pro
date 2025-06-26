from typing import Any, List

import pandas as pd
from pr_pro.sets import (
    WorkingSet_t,
    _build_metrics_list,
    _get_metric_config,
    create_sets_dataframe,
)
import streamlit as st


@st.cache_data
def st_create_sets_dataframe(_sets: List[WorkingSet_t]) -> pd.DataFrame:
    return create_sets_dataframe(_sets)


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
            'Set': st.column_config.TextColumn(width='small', pinned=True),
            'Reps': st.column_config.TextColumn(),
            'RPE': st.column_config.TextColumn(),
        },
    )
