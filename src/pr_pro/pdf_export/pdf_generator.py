from contextlib import contextmanager
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import TableBordersLayout
from fpdf.fonts import FontFace

from pr_pro.program import Program
from pr_pro.sets import WorkingSet_t, create_sets_dataframe
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession

PAGE_WIDTH_MM = 210.0
A4_HEIGHT_MM = 297.0
# PDF coordinates max out at 14400 pt (200 in); stay well under when measuring.
MAX_PAGE_HEIGHT_MM = 4000.0
# Keeps a snug page from tripping the mid-table page-break checks.
PAGE_HEIGHT_SLACK_MM = 5.0

MUTED_TEXT = (107, 114, 128)
TABLE_FONT_SIZE_PT = 9
# Booktabs-style rules: heavier above the headings and below the last row,
# hairline in between.
RULE_WIDTH_MM = 0.4
THIN_RULE_WIDTH_MM = 0.15
# Horizontal breathing room added to the widest string in a column. The slack covers
# the border line width, which fpdf2 takes out of the cell's text area.
COL_PADDING_MM = 2.0
COL_SLACK_MM = 1.0
# Floor for narrow columns such as 'Set', so they do not look cramped next to
# wider ones. Raise it to even the columns out, drop it to 0 to fit contents only.
MIN_COL_WIDTH_MM = 17.0
# Row height is the line height plus the vertical padding above and below it.
ROW_LINE_HEIGHT_MM = 3.6
ROW_PADDING_MM = 0.8
GROUP_GAP_MM = 8.0


class WorkoutPDF(FPDF):
    def __init__(self, page_format: str | tuple[float, float] = 'A4'):
        super().__init__(format=page_format)
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

    def add_session_link(self, label: str, link: int, indent: float = 0.0) -> None:
        """Write one clickable overview row that jumps to that session's page."""
        self.set_font('Arial', 'U', 11)
        self.set_text_color(0, 0, 200)
        self.set_x(self.l_margin + indent)
        self.cell(0, 7, label, 0, 1, 'L', link=link)
        self.set_text_color(0, 0, 0)

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
        self,
        exercise_name: str,
        sets: list[WorkingSet_t],
        part_of_group: bool = False,
    ) -> None:
        """Draw one exercise's sets as a booktabs-style table: no fills, no vertical
        rules, columns only as wide as their contents. Columns and value formatting
        come from create_sets_dataframe, shared with the Streamlit view."""
        df = create_sets_dataframe(sets)
        if df.empty:
            return

        col_widths = _column_widths(self, df)
        width = min(sum(col_widths), self.epw)

        if part_of_group:
            self.set_font('Arial', 'B', 10)
            self.cell(0, 7, exercise_name, 0, 1, 'L')
        else:
            self.add_heading(exercise_name, 3)

        self.set_font('Arial', '', TABLE_FONT_SIZE_PT)
        self.set_draw_color(0)
        self.set_line_width(THIN_RULE_WIDTH_MM)

        left = self.l_margin
        top = self.get_y()
        with self.table(
            align='LEFT',
            width=width,
            col_widths=col_widths,
            borders_layout=TableBordersLayout.SINGLE_TOP_LINE,
            headings_style=FontFace(emphasis='BOLD'),
            text_align='CENTER',
            line_height=ROW_LINE_HEIGHT_MM,
            padding=(ROW_PADDING_MM, COL_PADDING_MM),
        ) as table:
            header = table.row()
            for heading in df.columns:
                header.cell(str(heading))
            for values in df.itertuples(index=False):
                row = table.row()
                for value in values:
                    row.cell('' if value is None else str(value))

        # SINGLE_TOP_LINE only rules under the headings; booktabs also wants a rule
        # above them and one closing the table.
        self.set_line_width(RULE_WIDTH_MM)
        self.line(left, top, left + width, top)
        self.line(left, self.get_y(), left + width, self.get_y())
        self.set_line_width(THIN_RULE_WIDTH_MM)
        self.ln(2)

    def add_note(self, note: str, indent: float = 0.0) -> None:
        """Italic, muted note line under an exercise or group."""
        self.set_font('Arial', 'I', 9)
        self.set_text_color(*MUTED_TEXT)
        self.set_x(self.l_margin + indent)
        self.cell(0, 5, note, 0, 1, 'L')
        self.set_text_color(0)


def _column_widths(pdf: WorkoutPDF, df) -> list[float]:
    """Width each column needs for its widest entry, headings included."""
    widths = []
    for column in df.columns:
        pdf.set_font('Arial', 'B', TABLE_FONT_SIZE_PT)
        widest = pdf.get_string_width(str(column))
        pdf.set_font('Arial', '', TABLE_FONT_SIZE_PT)
        for value in df[column]:
            widest = max(widest, pdf.get_string_width(str(value)))
        content_width = widest + 2 * COL_PADDING_MM + COL_SLACK_MM
        widths.append(max(content_width, MIN_COL_WIDTH_MM))
    return widths


def _side_by_side_slots(
    pdf: WorkoutPDF,
    sets_per_exercise: list[tuple[object, list[WorkingSet_t]]],
    usable_width: float,
) -> list[float] | None:
    """Column widths for laying a group's tables out in a row, or None to stack them.

    Tables are already at their content width, so there is nothing to squeeze: they
    either fit beside each other or they do not.
    """
    slots = []
    for exercise, sets in sets_per_exercise:
        df = create_sets_dataframe(sets)
        if df.empty:
            return None
        pdf.set_font('Arial', 'B', 10)
        name_width = pdf.get_string_width(exercise.name) + COL_PADDING_MM
        slots.append(max(sum(_column_widths(pdf, df)), name_width))

    if sum(slots) + GROUP_GAP_MM * (len(slots) - 1) > usable_width:
        return None
    return slots


@contextmanager
def _column(pdf: WorkoutPDF, left: float, width: float):
    """Temporarily narrow the margins so a table renders inside one column slot."""
    saved = (pdf.l_margin, pdf.r_margin)
    pdf.l_margin, pdf.r_margin = left, pdf.w - (left + width)
    pdf.set_x(left)
    try:
        yield
    finally:
        pdf.l_margin, pdf.r_margin = saved
        pdf.set_x(pdf.l_margin)


def _render_session(pdf: WorkoutPDF, session: WorkoutSession) -> None:
    """Render one session's heading, stats and components at the current cursor."""
    pdf.add_heading(f'Session: {session.id}', level=2)

    if session.notes:
        pdf.add_note(session.notes)
    pdf.add_note(
        f'{session.get_number_of_exercises()} exercises  -  {session.get_number_of_sets()} sets'
    )
    pdf.ln(2)

    usable_width = pdf.w - 2 * pdf.l_margin

    for component in session.workout_components:
        if isinstance(component, SingleExercise):
            pdf.add_exercise_table(component.exercise.name, component.sets)
            if component.notes:
                pdf.add_note(component.notes)
            pdf.ln(2)

        elif isinstance(component, ExerciseGroup):
            pdf.add_heading(' + '.join(ex.name for ex in component.exercises), level=3)
            if component.notes:
                pdf.add_note(component.notes)
                pdf.ln(1)

            sets_per_exercise = [
                (exercise, component.exercise_sets_dict.get(exercise, []))
                for exercise in component.exercises
            ]
            slots = _side_by_side_slots(pdf, sets_per_exercise, usable_width)

            if slots is None:
                for exercise, sets in sets_per_exercise:
                    pdf.add_exercise_table(exercise.name, sets, part_of_group=True)
                    pdf.ln(1)
            else:
                top = pdf.get_y()
                left = pdf.l_margin
                bottoms = []
                for (exercise, sets), slot in zip(sets_per_exercise, slots):
                    pdf.set_y(top)
                    with _column(pdf, left, slot):
                        pdf.add_exercise_table(exercise.name, sets, part_of_group=True)
                    bottoms.append(pdf.get_y())
                    left += slot + GROUP_GAP_MM
                pdf.set_y(max(bottoms))

            pdf.ln(2)


def _overview_label(session: WorkoutSession) -> str:
    parts = [session.id]
    if session.notes:
        parts.append(session.notes)
    return '  -  '.join(parts)


def _session_height(session: WorkoutSession) -> float:
    """Render the session onto an oversized scratch page to learn how tall it is."""
    scratch = WorkoutPDF(page_format=(PAGE_WIDTH_MM, MAX_PAGE_HEIGHT_MM))
    scratch.set_auto_page_break(auto=False)
    scratch.add_page()
    top = scratch.get_y()
    _render_session(scratch, session)
    return scratch.get_y() - top


def export_program_to_pdf(program: Program, output_path: Path) -> None:
    """Export a workout program to PDF format"""
    pdf = WorkoutPDF()
    pdf.add_page()

    # Title
    pdf.add_title(program.name)

    # Best exercise values section
    if program.best_exercise_values:
        pdf.add_heading('Best Exercise Values / 1RM', level=1)
        for exercise, value in program.best_exercise_values.items():
            pdf.add_text(f'{exercise.name}: {value:g} kg', bold=False)
        pdf.ln(2)

    # Workout sessions
    pdf.add_heading('Workout Sessions', level=1)

    # One clickable row per session, grouped under the phase it belongs to. The targets
    # are empty until the session pages below are added, which is where they get resolved.
    links = {session_id: pdf.add_link() for session_id in program.workout_session_dict}

    phased: set[str] = set()
    for phase_name, session_ids in program.program_phases.items():
        pdf.add_text(phase_name, bold=True)
        for session_id in session_ids:
            session = program.workout_session_dict[session_id]
            pdf.add_session_link(_overview_label(session), links[session_id], indent=5)
            phased.add(session_id)
        pdf.ln(1)

    # Sessions outside any phase, which is every session when no phases are defined.
    for session_id, session in program.workout_session_dict.items():
        if session_id not in phased:
            pdf.add_session_link(_overview_label(session), links[session_id])
    pdf.ln(2)

    for session_id, session in program.workout_session_dict.items():
        content = _session_height(session)
        height = pdf.t_margin + content + pdf.b_margin + PAGE_HEIGHT_SLACK_MM
        pdf.add_page(format=(PAGE_WIDTH_MM, max(height, A4_HEIGHT_MM)))
        pdf.set_link(links[session_id], page=pdf.page_no())
        _render_session(pdf, session)

    # Save the PDF
    pdf.output(str(output_path))
