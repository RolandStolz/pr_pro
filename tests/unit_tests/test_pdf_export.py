import tempfile
from pathlib import Path

from pr_pro.configs import ComputeConfig
from pr_pro.example import get_simple_example_program
from pr_pro.functions import Brzycki1RMCalculator


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
