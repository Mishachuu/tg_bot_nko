from dataclasses import dataclass
from models.user import User

@dataclass
class Admin(User):
    """
    Класс администратора системы.
    
    Attributes:
        permissions (str): Разрешения администратора. 
            Возможно, лучше сделать отдельной структурой для гибкости.
    """
    permissions: str