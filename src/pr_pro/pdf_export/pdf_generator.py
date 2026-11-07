import io
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import NamedTuple

from fpdf import FPDF
from fpdf.enums import TableBordersLayout, XPos, YPos
from fpdf.fonts import FontFace

from pr_pro.program import Program
from pr_pro.sets import METRIC_LABELS, WorkingSet_t, create_sets_dataframe
from pr_pro.workout_component import ExerciseGroup, SingleExercise
from pr_pro.workout_session import WorkoutSession

PAGE_WIDTH_MM = 210.0
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
# A table never occupies less than this share of the width available to it; a
# two-column table would otherwise sit in a stub at the far left.
MIN_TABLE_WIDTH_FRACTION = 0.5
# A note belongs to the exercise above it, so it sits close to the heading and
# keeps a clear gap to the table below.
NOTE_LIFT_MM = 1.5
NOTE_GAP_BELOW_MM = 2.0
# Editable note box shown in place of the static note line.
NOTE_FIELD_HEIGHT_MM = 7.0
NOTE_FIELD_EDGE = (160, 160, 160)
PT_PER_MM = 72 / 25.4
# /Ff bit 13 is multiline, /F bit 3 marks the widget printable.
FIELD_FLAG_MULTILINE = 1 << 12
ANNOT_FLAG_PRINT = 1 << 2
GROUP_GAP_MM = 8.0


class NoteField(NamedTuple):
    """A reserved box, in fpdf2's mm-from-top-left coordinates."""

    name: str
    value: str
    page: int
    x: float
    y: float
    width: float
    height: float


class WorkoutPDF(FPDF):
    def __init__(
        self,
        page_format: str | tuple[float, float] = 'A4',
        excluded_columns: frozenset[str] = frozenset(),
        notes_field: bool = False,
    ):
        super().__init__(format=page_format)
        self.excluded_columns = excluded_columns
        self.notes_field = notes_field
        # Filled while rendering; the fillable widgets are attached after output,
        # because fpdf2 cannot write AcroForm fields itself.
        self.note_fields: list[NoteField] = []
        # No footer, so the bottom margin can match the top one.
        self.set_auto_page_break(auto=True, margin=self.t_margin)

    def sets_dataframe(self, sets: list[WorkingSet_t]):
        """The shared sets table, minus any metric this export was told to drop."""
        df = create_sets_dataframe(sets)
        dropped = [c for c in df.columns if c in self.excluded_columns]
        return df.drop(columns=dropped) if dropped else df

    def add_component_note(self, note: str | None, name: str) -> None:
        """A component's note: a static line, or an editable box when note fields
        are on. Either way it sits tight under the heading above it."""
        if not self.notes_field:
            if note:
                self.set_y(self.get_y() - NOTE_LIFT_MM)
                self.add_note(note)
                self.ln(NOTE_GAP_BELOW_MM)
            return

        x, y, width, height = self.l_margin, self.get_y(), self.epw, NOTE_FIELD_HEIGHT_MM
        self.set_draw_color(*NOTE_FIELD_EDGE)
        self.set_line_width(THIN_RULE_WIDTH_MM)
        self.rect(x, y, width, height)
        self.set_draw_color(0)

        self.note_fields.append(NoteField(name, note or '', self.page_no(), x, y, width, height))
        self.set_y(y + height)
        self.ln(NOTE_GAP_BELOW_MM)

    def add_title(self, title: str):
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 12, title, border=0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def add_heading(self, heading: str, level: int = 1):
        if level == 1:
            self.set_font('Helvetica', 'B', 16)
            self.ln(3)
        elif level == 2:
            self.set_font('Helvetica', 'B', 14)
            self.ln(2)
        else:
            self.set_font('Helvetica', 'B', 12)
            self.ln(1)

        if level != 1:
            self.start_section(heading, level - 1)

        self.cell(0, 8, heading, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if level == 2:
            self.line(10, self.get_y(), self.w - 10, self.get_y())

        self.ln(1)

    def add_text(self, text: str, bold: bool = False):
        font_style = 'B' if bold else ''
        self.set_font('Helvetica', font_style, 11)
        self.cell(0, 8, text, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_session_link(self, label: str, link: int, indent: float = 0.0) -> None:
        """Write one clickable overview row that jumps to that session's page."""
        self.set_font('Helvetica', 'U', 11)
        self.set_text_color(0, 0, 200)
        self.set_x(self.l_margin + indent)
        self.cell(0, 7, label, border=0, align='L', link=link, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def add_paragraph(self, text: str):
        self.set_font('Helvetica', '', 11)
        # Split long text into multiple lines
        lines = text.split('\n')
        for line in lines:
            if len(line) > 80:  # Wrap long lines
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + ' ' + word) > 80:
                        if current_line:
                            self.cell(
                                0,
                                6,
                                current_line.strip(),
                                border=0,
                                align='L',
                                new_x=XPos.LMARGIN,
                                new_y=YPos.NEXT,
                            )
                        current_line = word
                    else:
                        current_line += ' ' + word if current_line else word
                if current_line:
                    self.cell(
                        0,
                        6,
                        current_line.strip(),
                        border=0,
                        align='L',
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )
            else:
                self.cell(0, 6, line, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def add_exercise_table(
        self,
        exercise_name: str,
        sets: list[WorkingSet_t],
        note: str | None = None,
        note_name: str | None = None,
        part_of_group: bool = False,
    ) -> None:
        """Draw one exercise's sets as a booktabs-style table: no fills, no vertical
        rules, columns as wide as their contents, with the rules running the full
        width. Columns and value formatting come from create_sets_dataframe, shared
        with the Streamlit view."""
        df = self.sets_dataframe(sets)
        if df.empty:
            return

        col_widths = _column_widths(self, df)
        # Below the floor fpdf2 scales the columns up proportionally, so they stay
        # even with each other.
        width = min(max(sum(col_widths), self.epw * MIN_TABLE_WIDTH_FRACTION), self.epw)

        if part_of_group:
            self.set_font('Helvetica', 'B', 10)
            self.cell(0, 7, exercise_name, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.add_heading(exercise_name, 3)

        if note_name:
            self.add_component_note(note, note_name)
        elif note:
            self.set_y(self.get_y() - NOTE_LIFT_MM)
            self.add_note(note)
            self.ln(NOTE_GAP_BELOW_MM)

        self.set_font('Helvetica', '', TABLE_FONT_SIZE_PT)
        self.set_draw_color(0)
        self.set_line_width(THIN_RULE_WIDTH_MM)

        left = self.l_margin
        top = self.get_y()
        with self.table(
            align='LEFT',
            width=width,
            col_widths=col_widths,
            borders_layout=TableBordersLayout.NONE,
            headings_style=FontFace(emphasis='BOLD'),
            text_align='LEFT',
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

        # The table draws no rules of its own, so all three are drawn here, spanning
        # exactly the table's width.
        right = left + width
        headings_bottom = top + ROW_LINE_HEIGHT_MM + 2 * ROW_PADDING_MM
        self.set_line_width(RULE_WIDTH_MM)
        self.line(left, top, right, top)
        self.line(left, self.get_y(), right, self.get_y())
        self.set_line_width(THIN_RULE_WIDTH_MM)
        self.line(left, headings_bottom, right, headings_bottom)
        self.ln(2)

    def add_note(self, note: str, indent: float = 0.0) -> None:
        """Italic, muted note line under an exercise or group."""
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(*MUTED_TEXT)
        self.set_x(self.l_margin + indent)
        self.cell(0, 5, note, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0)


def _column_widths(pdf: WorkoutPDF, df) -> list[float]:
    """Width each column needs for its widest entry, headings included."""
    widths = []
    for column in df.columns:
        pdf.set_font('Helvetica', 'B', TABLE_FONT_SIZE_PT)
        widest = pdf.get_string_width(str(column))
        pdf.set_font('Helvetica', '', TABLE_FONT_SIZE_PT)
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

    Each slot is only as wide as its own table, so the tables sit next to each
    other with just the gap between them rather than spread across the page.
    """
    slots = []
    for exercise, sets in sets_per_exercise:
        df = pdf.sets_dataframe(sets)
        if df.empty:
            return None
        pdf.set_font('Helvetica', 'B', 10)
        name_width = pdf.get_string_width(exercise.name) + COL_PADDING_MM
        slots.append(max(sum(_column_widths(pdf, df)), name_width))

    if sum(slots) > usable_width - GROUP_GAP_MM * (len(slots) - 1):
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

    for index, component in enumerate(session.workout_components, start=1):
        note_name = f'notes_{session.id}_{index}'

        if isinstance(component, SingleExercise):
            pdf.add_exercise_table(
                component.exercise.name,
                component.sets,
                note=component.notes,
                note_name=note_name,
            )
            pdf.ln(2)

        elif isinstance(component, ExerciseGroup):
            pdf.add_heading(' + '.join(ex.name for ex in component.exercises), level=3)
            pdf.add_component_note(component.notes, note_name)

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
                for (exercise, sets), slot in zip(sets_per_exercise, slots, strict=True):
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


def _content_height(pdf: WorkoutPDF, render: Callable[[WorkoutPDF], None]) -> float:
    """Run the drawing onto an oversized scratch page to learn how tall it is.

    The scratch page mirrors the real one's options so the two agree on height.
    """
    scratch = WorkoutPDF(
        page_format=(PAGE_WIDTH_MM, MAX_PAGE_HEIGHT_MM),
        excluded_columns=pdf.excluded_columns,
        notes_field=pdf.notes_field,
    )
    scratch.set_auto_page_break(auto=False)
    scratch.add_page()
    top = scratch.get_y()
    render(scratch)
    return scratch.get_y() - top


def _add_fitted_page(pdf: WorkoutPDF, content_height: float) -> None:
    """Start a page just tall enough for that much content, plus the margins."""
    height = pdf.t_margin + content_height + pdf.b_margin + PAGE_HEIGHT_SLACK_MM
    pdf.add_page(format=(PAGE_WIDTH_MM, height))


def _render_overview(pdf: WorkoutPDF, program: Program, links: dict[str, int]) -> None:
    """Title, best values, and one clickable row per session grouped by phase."""
    pdf.add_title(program.name)

    if program.best_exercise_values:
        pdf.add_heading('Best Exercise Values / 1RM', level=1)
        for exercise, value in program.best_exercise_values.items():
            pdf.add_text(f'{exercise.name}: {value:g} kg', bold=False)
        pdf.ln(2)

    pdf.add_heading('Workout Sessions', level=1)

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


def _attach_note_fields(output_path: Path, note_fields: list[NoteField]) -> None:
    """Rewrite the file with a fillable multiline text field over each reserved box.

    fpdf2 has no AcroForm support, so the widgets are added afterwards with pypdf.
    NeedAppearances asks the viewer to render whatever the reader types, since the
    fields ship without appearance streams of their own.
    """
    from pypdf import PdfWriter
    from pypdf.generic import (
        ArrayObject,
        BooleanObject,
        DictionaryObject,
        FloatObject,
        NameObject,
        NumberObject,
        TextStringObject,
    )

    writer = PdfWriter(clone_from=io.BytesIO(output_path.read_bytes()))
    references = []
    for field in note_fields:
        page = writer.pages[field.page - 1]
        # fpdf2 measures mm down from the top left; PDF measures points up from the
        # bottom left, and each page here has its own height.
        page_top = float(page.mediabox.height)
        rect = [
            field.x * PT_PER_MM,
            page_top - (field.y + field.height) * PT_PER_MM,
            (field.x + field.width) * PT_PER_MM,
            page_top - field.y * PT_PER_MM,
        ]
        widget = DictionaryObject(
            {
                NameObject('/Type'): NameObject('/Annot'),
                NameObject('/Subtype'): NameObject('/Widget'),
                NameObject('/FT'): NameObject('/Tx'),
                NameObject('/T'): TextStringObject(field.name),
                NameObject('/V'): TextStringObject(field.value),
                NameObject('/Ff'): NumberObject(FIELD_FLAG_MULTILINE),
                NameObject('/F'): NumberObject(ANNOT_FLAG_PRINT),
                NameObject('/Rect'): ArrayObject([FloatObject(value) for value in rect]),
                NameObject('/DA'): TextStringObject('/Helv 9 Tf 0 g'),
            }
        )
        added = writer.add_annotation(page_number=field.page - 1, annotation=widget)
        references.append(added.indirect_reference)

    helvetica = DictionaryObject(
        {
            NameObject('/Type'): NameObject('/Font'),
            NameObject('/Subtype'): NameObject('/Type1'),
            NameObject('/BaseFont'): NameObject('/Helvetica'),
            NameObject('/Encoding'): NameObject('/WinAnsiEncoding'),
        }
    )
    writer._root_object[NameObject('/AcroForm')] = DictionaryObject(
        {
            NameObject('/Fields'): ArrayObject(references),
            NameObject('/DA'): TextStringObject('/Helv 9 Tf 0 g'),
            NameObject('/DR'): DictionaryObject(
                {NameObject('/Font'): DictionaryObject({NameObject('/Helv'): helvetica})}
            ),
            NameObject('/NeedAppearances'): BooleanObject(True),
        }
    )

    # Give the pre-filled notes an appearance stream. NeedAppearances alone leaves
    # them blank in viewers that ignore it, which would hide real content.
    by_page: dict[int, dict[str, str]] = {}
    for field in note_fields:
        if field.value:
            by_page.setdefault(field.page, {})[field.name] = field.value
    for page_number, values in by_page.items():
        writer.update_page_form_field_values(writer.pages[page_number - 1], values)

    writer.write(output_path)


def export_program_to_pdf(
    program: Program,
    output_path: Path,
    exclude_metrics: Iterable[str] = (),
    notes_field: bool = False,
) -> None:
    """Export a workout program to PDF format.

    exclude_metrics names set fields to leave out of the tables, for example
    'relative_percentage' or 'rest_between'. Unknown names raise ValueError rather
    than being ignored, since a typo would otherwise silently keep the column.

    notes_field adds an empty, fillable text box at the end of each session page
    that the reader can type into and save from a PDF viewer.
    """
    exclude_metrics = list(exclude_metrics)
    unknown = sorted(set(exclude_metrics) - set(METRIC_LABELS))
    if unknown:
        raise ValueError(f'Unknown metric(s) {unknown}. Choose from {sorted(METRIC_LABELS)}.')

    pdf = WorkoutPDF(
        excluded_columns=frozenset(METRIC_LABELS[metric] for metric in exclude_metrics),
        notes_field=notes_field,
    )

    # add_link() binds to the current page, so every link is made after a page exists:
    # throwaway ones in the scratch pass, the real ones once page 1 is open. Their
    # targets stay empty until the session pages are added further down.
    _add_fitted_page(
        pdf,
        _content_height(
            pdf,
            lambda scratch: _render_overview(
                scratch,
                program,
                {session_id: scratch.add_link() for session_id in program.workout_session_dict},
            ),
        ),
    )
    links = {session_id: pdf.add_link() for session_id in program.workout_session_dict}
    _render_overview(pdf, program, links)

    for session_id, session in program.workout_session_dict.items():
        # partial, not a lambda: it binds this session now, so the closure cannot
        # pick up a later loop value (ruff B023).
        _add_fitted_page(pdf, _content_height(pdf, partial(_render_session, session=session)))
        pdf.set_link(links[session_id], page=pdf.page_no())
        _render_session(pdf, session)

    # Save the PDF
    output_path = Path(output_path)
    pdf.output(str(output_path))
    if pdf.note_fields:
        _attach_note_fields(output_path, pdf.note_fields)
