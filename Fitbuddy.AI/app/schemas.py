
from pydantic import BaseModel, Field
from typing import Literal


class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=100)

    goal: Literal[
        "general_wellness",
        "strength",
        "flexibility",
        "energy"
    ]

    intensity: Literal["low", "medium", "high"]


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str = Field(min_length=3, max_length=1000)