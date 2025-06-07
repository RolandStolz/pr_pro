import streamlit as st
import json
import os

DATA_FILE = 'app_state.json'
_PERSISTED_SESSION_STATE_KEYS = '_persisted_checkbox_keys_'


def load_persisted_state_from_file():
    """
    Loads checkbox states (and other registered persistent states)
    from the JSON file into st.session_state.
    This should be called once when the app/page loads.
    """
    if _PERSISTED_SESSION_STATE_KEYS not in st.session_state:
        st.session_state[_PERSISTED_SESSION_STATE_KEYS] = set()

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                persisted_data = json.load(f)

            # Load the set of keys that were persisted
            persisted_keys_list = persisted_data.get(_PERSISTED_SESSION_STATE_KEYS, [])
            st.session_state[_PERSISTED_SESSION_STATE_KEYS].update(persisted_keys_list)

            for key in st.session_state[_PERSISTED_SESSION_STATE_KEYS]:
                if key in persisted_data:
                    st.session_state[key] = persisted_data[key]

        except json.JSONDecodeError:
            st.warning(
                f'Could not decode state file {DATA_FILE}. Starting with/using default states.'
            )
        except Exception as e:
            st.error(f'Error loading state from {DATA_FILE}: {e}')

    for key in list(st.session_state[_PERSISTED_SESSION_STATE_KEYS]):
        if key not in st.session_state:
            value = '' if key.endswith('_comment') else False
            st.session_state[key] = value


def save_persisted_state_to_file():
    """
    Saves the current state of registered checkboxes (and other persistent states)
    from st.session_state to the JSON file.
    This is typically called via on_change callbacks.
    """
    data_to_save = {}
    if _PERSISTED_SESSION_STATE_KEYS not in st.session_state:
        st.session_state[_PERSISTED_SESSION_STATE_KEYS] = set()

    data_to_save[_PERSISTED_SESSION_STATE_KEYS] = list(
        st.session_state[_PERSISTED_SESSION_STATE_KEYS]
    )

    for key in st.session_state[_PERSISTED_SESSION_STATE_KEYS]:
        if key in st.session_state:
            data_to_save[key] = st.session_state[key]

    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        st.error(f'Error saving state to {DATA_FILE}: {e}')


def register_key_for_persistence(key: str, default_value: bool | str = False):
    """
    Registers a key from st.session_state to be persisted.
    Also initializes it in st.session_state if it's not already present (e.g., from file load).
    """
    if _PERSISTED_SESSION_STATE_KEYS not in st.session_state:
        st.session_state[_PERSISTED_SESSION_STATE_KEYS] = set()

    st.session_state[_PERSISTED_SESSION_STATE_KEYS].add(key)

    if key not in st.session_state:
        st.session_state[key] = default_value
