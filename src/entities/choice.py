from dataclasses import dataclass
from uuid import UUID
from .base import BaseEntity


@dataclass
class Choice(BaseEntity):
    question_uuid: UUID  # fk to question
    choice_text: str
    votes: int = 0
