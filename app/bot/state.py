from dataclasses import dataclass, field
from typing import Optional, Set, Dict, Any


@dataclass
class UserState:
    state: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchState:
    selected_categories: Set[int] = field(default_factory=set)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    radius_km: int = 30

