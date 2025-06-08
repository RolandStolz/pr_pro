from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from pr_pro.functions import Brzycki1RMCalculator, OneRMCalculator


class ComputeConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    one_rm_calculator: OneRMCalculator = Brzycki1RMCalculator()

    # Store associations, so the values ofr one exercise can be derived from the max of another
    # Cannot give type hint due to circular imports ...
    exercise_associations: dict = {}
