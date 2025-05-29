from pr_pro.functions import Brzycki1RMCalculator, OneRMCalculator


from pydantic import BaseModel


class ComputeConfig(BaseModel):
    one_rm_calculator: OneRMCalculator = Brzycki1RMCalculator()
