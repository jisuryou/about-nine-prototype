from dataclasses import dataclass
from typing import List


@dataclass
class Utterance:
    speaker: str
    start: float
    end: float
    text: str


@dataclass
class Conversation:
    call_id: str
    conversation: List[Utterance]
