from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, String
from sqlmodel import Field, SQLModel

from logic.base import EvaluationResult, MatchResult


class PvE(SQLModel, table=True):
    __tablename__ = "pve_game"  # type: ignore[assignment]

    id: str = Field(default_factory=lambda: uuid4().__str__(), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    user_id: str

    bot_deck: list[str] = Field(sa_column=Column(JSON))
    bot_evaluation: EvaluationResult = Field(sa_column=Column(String))

    user_deck: list[str] = Field(sa_column=Column(JSON))
    user_evaluation: EvaluationResult = Field(sa_column=Column(String))

    winner: MatchResult = Field(sa_column=Column(String))