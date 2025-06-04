try:
    import streamlit  # noqa: F401
except ImportError:
    raise ImportError(
        'streamlit is not installed. Please install the `vis` extra as `pip install pr_pro[vis]`.'
    )
