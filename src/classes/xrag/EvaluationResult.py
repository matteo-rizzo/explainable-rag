from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    classification: str = Field(
        ...,
        description="The classification label indicating whether the contract is 'Reentrant' or 'Safe'."
    )
    explanation: str = Field(
        ...,
        description="A detailed explanation for the classification, citing specific lines or functions in the contract as evidence."
    )
