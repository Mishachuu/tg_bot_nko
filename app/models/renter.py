from dataclasses import dataclass
from models.user import User
from models.contact import Contact

@dataclass
class Renter(User):
    rented_items: list
    contact: Contact
    location: str