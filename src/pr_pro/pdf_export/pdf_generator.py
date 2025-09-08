from pathlib import Path
from fpdf import FPDF
from pr_pro.program import Program
from pr_pro.workout_component import SingleExercise, ExerciseGroup


class WorkoutPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo or header content could go here
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_title(self, title: str):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 12, title, 0, 1, 'C')
        self.ln(3)

    def add_heading(self, heading: str, level: int = 1):
        if level == 1:
            self.set_font('Arial', 'B', 16)
            self.ln(3)
        elif level == 2:
            self.set_font('Arial', 'B', 14)
            self.ln(2)
        else:
            self.set_font('Arial', 'B', 12)
            self.ln(1)

        if level != 1:
            self.start_section(heading, level - 1)

        self.cell(0, 8, heading, 0, 1, 'L')
        if level == 2:
            self.line(10, self.get_y(), self.w - 10, self.get_y())

        self.ln(1)

    def add_text(self, text: str, bold: bool = False):
        font_style = 'B' if bold else ''
        self.set_font('Arial', font_style, 11)
        self.cell(0, 8, text, 0, 1, 'L')

    def add_paragraph(self, text: str):
        self.set_font('Arial', '', 11)
        # Split long text into multiple lines
        lines = text.split('\n')
        for line in lines:
            if len(line) > 80:  # Wrap long lines
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + ' ' + word) > 80:
                        if current_line:
                            self.cell(0, 6, current_line.strip(), 0, 1, 'L')
                        current_line = word
                    else:
                        current_line += ' ' + word if current_line else word
                if current_line:
                    self.cell(0, 6, current_line.strip(), 0, 1, 'L')
            else:
                self.cell(0, 6, line, 0, 1, 'L')
        self.ln(2)

    def add_exercise_table(
        self, exercise_name, sets_data, table_width=None, start_x=None, part_of_group=False
    ):
        """Add a table for an exercise with its sets."""
        if table_width is None:
            table_width = self.w - 2 * self.l_margin

        if start_x is None:
            start_x = self.l_margin

        # Collect columns from the actual sets data (exercise-specific)
        column_names = set()
        for set_dict in sets_data:
            column_names.update(set_dict.keys())

        # Enforce ordering with reps first
        ordered_columns = []
        if 'reps' in column_names:
            ordered_columns.append('reps')
            column_names.remove('reps')

        # Add remaining columns in sorted order
        ordered_columns.extend(sorted(column_names))
        column_names = ordered_columns

        display_column_names = []
        for col in column_names:
            if col == 'percentage':
                display_column_names.append('Abs %')
            elif col == 'relative_percentage':
                display_column_names.append('Rel %')
            else:
                display_column_names.append(col.replace('_', ' ').title())

        # Calculate column width
        col_width = table_width / len(column_names)

        # Check if we need a new page for the table header + at least one row
        # min_height_needed = 8 + 2 + 6 + 6  # title + spacing + header + one data row
        # if self.get_y() + min_height_needed > self.h - self.b_margin:
        #     self.add_page()

        # Exercise name header
        if part_of_group:
            self.set_font('Arial', 'B', 10)
            self.set_x(start_x)
            self.cell(table_width, 8, exercise_name, 0, 1, 'L')
            self.ln(1)
        else:
            self.add_heading(exercise_name, 3)
            self.ln(2)

        # Table header
        self.set_font('Arial', 'B', 10)
        self.set_x(start_x)

        for display_col in display_column_names:
            self.cell(col_width, 6, display_col, 1, 0, 'C')
        self.ln()

        # Table data
        self.set_font('Arial', '', 10)
        for set_dict in sets_data:
            # Check if we need a new page for this row
            if self.get_y() + 6 > self.h - self.b_margin:
                self.add_page()
                # Redraw header on new page
                self.set_font('Arial', 'B', 10)
                self.set_x(start_x)
                for display_col in display_column_names:
                    self.cell(col_width, 6, display_col, 1, 0, 'C')
                self.ln()
                self.set_font('Arial', '', 10)

            self.set_x(start_x)
            for col in column_names:
                value = set_dict.get(col, '')
                if isinstance(value, float):
                    # value = f'{value:.1f}'
                    # value = f'{value}'
                    # Check if value is decimal
                    value = round(value, 3)

                self.cell(col_width, 6, str(value), 1, 0, 'C')
            self.ln()

        self.ln(3)


def export_program_to_pdf(program: Program, output_path: Path) -> None:
    """Export a workout program to PDF format"""
    pdf = WorkoutPDF()
    pdf.add_page()

    # Title
    pdf.add_title(program.name)

    # Best exercise values section
    if program.best_exercise_values:
        pdf.add_heading('Best Exercise Values', level=1)
        for exercise, value in program.best_exercise_values.items():
            pdf.add_text(f'{exercise.name}: {value} kg', bold=False)
        pdf.ln(2)

    # Program phases (if any)
    if program.program_phases:
        pdf.add_heading('Program Phases', level=1)
        for phase_name, session_ids in program.program_phases.items():
            pdf.add_text(f'{phase_name}: {", ".join(session_ids)}', bold=True)
        pdf.ln(2)

    # Workout sessions
    pdf.add_heading('Workout Sessions', level=1)

    for session_id, session in program.workout_session_dict.items():
        pdf.add_heading(f'Session: {session.id}', level=2)

        if session.notes:
            pdf.add_text(f'Notes: {session.notes}')
            pdf.ln(1)

        # Session stats
        pdf.add_text(
            f'Exercises: {session.get_number_of_exercises()}, Sets: {session.get_number_of_sets()}'
        )
        pdf.ln(2)

        # Components
        for component in session.workout_components:
            if isinstance(component, SingleExercise):
                # Convert sets to dict format for table
                sets_data = []
                for workout_set in component.sets:
                    set_dict = workout_set.model_dump()
                    # Filter out None values and rest_between
                    set_dict = {
                        k: v for k, v in set_dict.items() if v is not None and k != 'rest_between'
                    }
                    sets_data.append(set_dict)

                # Use full page width for single exercises
                full_width = pdf.w - 2 * pdf.l_margin
                pdf.add_exercise_table(component.exercise.name, sets_data, table_width=full_width)

                # Add notes underneath if provided
                if component.notes:
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 6, f'Notes: {component.notes}', 0, 1, 'L')

                pdf.ln(2)

            elif isinstance(component, ExerciseGroup):
                group_title = ' + '.join([ex.name for ex in component.exercises])
                pdf.add_heading(group_title, level=3)

                # Add group notes underneath if provided
                if component.notes:
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 6, f'Notes: {component.notes}', 0, 1, 'L')
                    pdf.ln(1)

                # For exercise groups with 2 exercises, place side by side
                if len(component.exercises) == 2:
                    # Collect sets data for each exercise individually (no unified columns)
                    all_sets_data = {}

                    for exercise in component.exercises:
                        sets = component.exercise_sets_dict.get(exercise, [])
                        sets_data = []
                        for workout_set in sets:
                            set_dict = workout_set.model_dump()
                            set_dict = {
                                k: v
                                for k, v in set_dict.items()
                                if v is not None and k != 'rest_between'
                            }
                            sets_data.append(set_dict)
                        all_sets_data[exercise] = sets_data

                    # Estimate table height to check if it fits on current page
                    # Use the exercise with more sets for height estimation
                    max_sets = max(len(data) for data in all_sets_data.values())
                    estimated_table_height = 6 + (max_sets + 1) * 7  # header + data rows
                    current_y = pdf.get_y()
                    page_height = pdf.h - pdf.b_margin

                    # If tables won't fit on current page, start a new page
                    if current_y + estimated_table_height > page_height:
                        pdf.add_page()

                    # Calculate table positioning for side-by-side layout
                    table_width = (
                        pdf.w - 2 * pdf.l_margin - 10
                    ) / 2  # Leave some margin between tables
                    start_y = pdf.get_y()

                    # First exercise table (left side) - use only its own columns
                    exercise = component.exercises[0]
                    pdf.add_exercise_table(
                        exercise.name,
                        all_sets_data[exercise],
                        table_width=table_width,
                        start_x=pdf.l_margin,
                        part_of_group=True,
                    )
                    first_table_bottom = pdf.get_y()

                    # Second exercise table (right side) - use only its own columns
                    pdf.set_y(start_y)  # Reset to same Y position
                    exercise = component.exercises[1]
                    second_table_start_x = pdf.l_margin + table_width + 10
                    pdf.add_exercise_table(
                        exercise.name,
                        all_sets_data[exercise],
                        table_width=table_width,
                        start_x=second_table_start_x,
                        part_of_group=True,
                    )
                    second_table_bottom = pdf.get_y()

                    # Move to bottom of both tables
                    pdf.set_y(max(first_table_bottom, second_table_bottom))
                else:
                    # For other cases, stack vertically
                    for exercise in component.exercises:
                        sets = component.exercise_sets_dict.get(exercise, [])
                        sets_data = []
                        for workout_set in sets:
                            set_dict = workout_set.model_dump()
                            set_dict = {
                                k: v
                                for k, v in set_dict.items()
                                if v is not None and k != 'rest_between'
                            }
                            sets_data.append(set_dict)

                        full_width = pdf.w - 2 * pdf.l_margin
                        pdf.add_exercise_table(exercise.name, sets_data, table_width=full_width)
                        pdf.ln(1)

                pdf.ln(2)

        # Add page break between sessions if not the last one
        # session_ids = list(program.workout_session_dict.keys())
        # if session_id != session_ids[-1]:
        #     pdf.add_page()

    # Save the PDF
    pdf.output(str(output_path))
