from datetime import datetime
from dataclasses import dataclass
from .base import BaseEntity


@dataclass
class Question(BaseEntity):
    question_text: str
    pub_date: datetime
