from pydantic import BaseModel, ConfigDict
from pr_pro.functions import Brzycki1RMCalculator, OneRMCalculator


class ComputeConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    one_rm_calculator: OneRMCalculator = Brzycki1RMCalculator()
