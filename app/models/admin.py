from dataclasses import dataclass

@dataclass
class Admin():
    """
    Класс администратора системы.
    
    Attributes:
        permissions (str): Разрешения администратора. 
            Возможно, лучше сделать отдельной структурой для гибкости.
    """
    permissions: str