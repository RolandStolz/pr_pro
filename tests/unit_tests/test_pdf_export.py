import tempfile
from pathlib import Path

import pytest

from pr_pro.configs import ComputeConfig
from pr_pro.example import get_example_program, get_simple_example_program
from pr_pro.functions import Brzycki1RMCalculator


def extract_text(path: Path) -> str:
    from pypdf import PdfReader

    return '\n'.join(page.extract_text() for page in PdfReader(path).pages)


def test_pdf_export():
    """Test that PDF export works without errors"""
    program = get_simple_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_program.pdf'

        # Should not raise any exceptions
        program.export_to_pdf(output_path)

        # Check that file was created and has content
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_one_page_per_session():
    """Each session gets exactly one page, however tall its content."""
    program = get_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))

    # Overgrow one session so its content cannot fit on A4.
    big = next(iter(program.workout_session_dict.values()))
    big.workout_components = big.workout_components * 4

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_program.pdf'
        program.export_to_pdf(output_path)

        raw = output_path.read_bytes()
        pages = raw.count(b'/Type /Page') - raw.count(b'/Type /Pages')
        # One overview page plus one page per session.
        assert pages == len(program.workout_session_dict) + 1


def test_session_links_target_session_pages():
    """Every overview row links to the page its session was rendered on."""
    from pypdf import PdfReader

    program = get_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_program.pdf'
        program.export_to_pdf(output_path)

        reader = PdfReader(output_path)
        page_number = {page.indirect_reference.idnum: i + 1 for i, page in enumerate(reader.pages)}
        targets = [
            page_number[annotation.get_object()['/Dest'][0].idnum]
            for page in reader.pages
            for annotation in page.get('/Annots', [])
            if annotation.get_object().get('/Subtype') == '/Link'
        ]

        # Every session page is linked to. A session listed in two phases gets two rows,
        # so compare the distinct targets.
        session_count = len(program.workout_session_dict)
        distinct = sorted(set(targets))
        assert len(distinct) == session_count
        assert distinct == list(range(distinct[0], distinct[0] + session_count))
        # Sessions start after the overview, never on it.
        assert distinct[0] > 1


def test_exclude_metrics_drops_columns():
    """Excluded metrics disappear from the tables; the rest are untouched."""
    program = get_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))

    with tempfile.TemporaryDirectory() as temp_dir:
        full = Path(temp_dir) / 'full.pdf'
        trimmed = Path(temp_dir) / 'trimmed.pdf'
        program.export_to_pdf(full)
        program.export_to_pdf(trimmed, exclude_metrics=['relative_percentage'])

        full_text = extract_text(full)
        trimmed_text = extract_text(trimmed)

        assert 'Rel %' in full_text
        assert 'Rel %' not in trimmed_text
        # The other metrics still render.
        for heading in ('Set', 'Reps', 'Weight', 'Abs %'):
            assert heading in trimmed_text


def test_exclude_metrics_rejects_unknown_name():
    program = get_example_program()
    program.compute_values(ComputeConfig(one_rm_calculator=Brzycki1RMCalculator()))

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError, match='rel_percentage'):
            program.export_to_pdf(Path(temp_dir) / 'x.pdf', exclude_metrics=['rel_percentage'])
