import pytest
from pr_pro.configs import ComputeConfig
from pr_pro.functions import OneRMCalculator
from pr_pro.sets import PowerExerciseSet, RepsAndWeightsSet


class MockOneRMCalculator(OneRMCalculator):
    """
    A mock calculator with simple, predictable formulas for testing.
    - 1RM = weight * (1 + 0.1 * reps)
    - Weight = 1RM / (1 + 0.1 * reps)
    """

    def one_rep_max(self, weight: float, reps: int) -> float:
        return weight * (1 + 0.1 * reps)

    def max_weight_from_reps(self, one_rm: float, reps: int) -> float:
        return one_rm / (1 + 0.1 * reps)

    def max_reps_from_weight(self, one_rm_weight: float, weight: float) -> float:
        return 10 * ((one_rm_weight / weight) - 1)


@pytest.fixture
def mock_config() -> ComputeConfig:
    """A pytest fixture that provides a ComputeConfig with our mock calculator."""
    return ComputeConfig(one_rm_calculator=MockOneRMCalculator())


class TestRepsAndWeightsSetComputeValues:
    """Unit tests for the RepsAndWeightsSet.compute_values method."""

    def test_calculates_percentage_from_weight(self, mock_config):
        """Given only weight, it should calculate percentage."""
        work_set = RepsAndWeightsSet(reps=5, weight=80)
        work_set.compute_values(100.0, mock_config)

        assert work_set.weight == 80.0
        assert work_set.percentage == pytest.approx(0.8)

    def test_calculates_weight_from_percentage(self, mock_config):
        """Given only percentage, it should calculate weight."""
        work_set = RepsAndWeightsSet(reps=5, percentage=0.75)
        work_set.compute_values(100.0, mock_config)

        assert work_set.percentage == 0.75
        assert work_set.weight == pytest.approx(75.0)

    def test_calculates_relative_percentage(self, mock_config):
        """Given weight and reps, it should calculate relative_percentage."""
        work_set = RepsAndWeightsSet(reps=5, weight=80)
        work_set.compute_values(100.0, mock_config)

        assert work_set.relative_percentage == pytest.approx(1.2)

    def test_calculates_weights_from_relative_percentage(self, mock_config):
        """Given only relative_percentage, it should calculate weight and percentage."""
        work_set = RepsAndWeightsSet(reps=5, relative_percentage=1.1)
        work_set.compute_values(100.0, mock_config)

        assert work_set.weight == pytest.approx(73.333, rel=1e-5)
        assert work_set.percentage == pytest.approx(0.73333, rel=1e-5)

    def test_raises_assertion_on_inconsistent_weight_and_percentage(self, mock_config):
        """It should raise an AssertionError if provided weight and percentage conflict."""
        # 80kg should be 80% of 100, not 70%
        work_set = RepsAndWeightsSet(reps=5, weight=80, percentage=0.7)
        with pytest.raises(AssertionError):
            work_set.compute_values(100.0, mock_config)


class TestPowerExerciseSetComputeValues:
    """Unit tests for the PowerExerciseSet.compute_values method."""

    def test_calculates_percentage_from_weight(self, mock_config):
        """Given only weight, it should calculate percentage."""
        work_set = PowerExerciseSet(reps=3, weight=50)
        work_set.compute_values(100.0, mock_config)

        assert work_set.weight == 50.0
        assert work_set.percentage == pytest.approx(0.5)

    def test_calculates_weight_from_percentage(self, mock_config):
        """Given only percentage, it should calculate weight."""
        work_set = PowerExerciseSet(reps=3, percentage=0.6)
        work_set.compute_values(100.0, mock_config)

        assert work_set.percentage == 0.6
        assert work_set.weight == pytest.approx(60.0)

    def test_raises_assertion_on_inconsistent_weight_and_percentage(self, mock_config):
        """It should raise an AssertionError if provided weight and percentage conflict."""
        work_set = PowerExerciseSet(reps=3, weight=60, percentage=0.5)
        with pytest.raises(AssertionError):
            work_set.compute_values(100.0, mock_config)

    def test_assertion_logic_on_consistent_values(self, mock_config):
        """
        Tests that the assertion passes with consistent values.
        """
        work_set = PowerExerciseSet(reps=3, weight=60, percentage=0.6)
        work_set.compute_values(100.0, mock_config)
