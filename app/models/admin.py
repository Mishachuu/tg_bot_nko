from dataclasses import dataclass
from models.user import User

@dataclass
class Admin(User):
    permissions: str #наверное лучше структурой сделать отдельной разрешения
