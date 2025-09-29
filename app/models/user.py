from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    tg_id: int