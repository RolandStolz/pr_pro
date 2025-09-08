# PRogramming PROgrams
---
[![cov](https://RolandStolz.github.io/pr_pro/badges/coverage.svg)](https://github.com/RolandStolz/pr_pro/actions)

`pr_pro` is a Python package for defining training programs. It's main features at a glance are:
1. Modular and extensible definition of different types of exercises
2. Export to and import from `json` files
3. Automatic computation of weights based on defined max values
3. Render as **plain text** or **pdf**
4. **Ready to deploy** `streamlit` app for each custom program that you define

## Simple example
```Python
program = get_simple_example_program()
program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))
print(program)

# Export to pdf
program.export_to_pdf(Path('example.pdf'))
```
```
--- Workout Test program ---
Best exercise values
  Backsquat: 100
  Bench Press: 80

Workout sessions
--- W1D1 ---
notes: Easy on first day.
Backsquat with 2 sets:
  reps 5, weight 55.0, percentage 0.55, relative_percentage 0.619
  reps 5, weight 55.0, percentage 0.55, relative_percentage 0.619
Pendlay row + Pushup with 2 sets:
  reps 6, percentage 0.6 | reps 10
  reps 6, percentage 0.6 | reps 10
Bench Press with 2 sets:
  reps 8, weight 40.0, percentage 0.5, relative_percentage 0.621
  reps 8, weight 40.0, percentage 0.5, relative_percentage 0.621
```

`pr_pro` also allows defining progressions throughout the training block. Look into `pr_pro/examples.py` for an example of this.

## Installation
```bash
pip install pr_pro
```

## `streamlit` visualization
You need to install the visualization dependencies
```bash
pip install pr_pro[vis]
```

Simply define your program and create a file `streamlit_app.py` with
```python
from pr_pro.streamlit_vis.streamlit_app import run_streamlit_app

program = ...  # Your program
run_streamlit_app(program)
```

Then run the streamlit app as per usual
```bash
streamlit run streamlit_app.py
```

The app looks like this:
![Streamlit app example](https://RolandStolz.github.io/pr_pro/streamlit_app_example.png)

For a live demo go to [https://pr-pro-demo.streamlit.app/](https://pr-pro-demo.streamlit.app/)
