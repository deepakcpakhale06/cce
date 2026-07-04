from pydantic import BaseModel
from typing import Literal

LLMProvider = Literal['local']

class EstimateRow(BaseModel):
    id: str
    componentName: str
    awsServiceName: str
    quantity: int
    configuration: str
    assumptions: str
    costPerMonth: float = 0.0
    yearlyCost: float = 0.0

class Estimate(BaseModel):
    rows: list[EstimateRow]

class AnalyzeRequest(BaseModel):
    description: str
    region: str

class PricingRequest(BaseModel):
    rows: list[EstimateRow]
    region: str

class CalculatorLinkRequest(BaseModel):
    description: str | None = None
    rows: list[EstimateRow] = []
    region: str
    estimate_name: str = 'AWS Cost Estimator'
