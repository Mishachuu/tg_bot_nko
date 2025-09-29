from dataclasses import dataclass
from models.user import User
from models.contact import Contact

@dataclass
class Owner(User):
    property_list: list
    contact: Contact
