from typing import List, Optional
from models.owner import Owner
from repositories.landlord_repository import LandlordRepository
from app.repositories.booking_repository import BookingRepository


class LandlordService:
    """
    Сервис для работы с арендодателями (Owner).
    Инкапсулирует бизнес-логику и обращается к LandlordRepository и BookingRepository.
    """

    def __init__(self, repository: Optional[LandlordRepository] = None):
        self.repository = repository or LandlordRepository()
        self.booking_repo = BookingRepository()

    async def create_landlord(
        self,
        name: str,
        phone_numbers: List[str],
        emails: List[str],
        equipment_list: List[str] = None,
        score: float = 0.0,
    ) -> Owner:
        equipment_list = equipment_list or []

        new_owner = Owner(
            name=name,
            phone_numbers=phone_numbers,
            emails=emails,
            equipment_list=equipment_list,
            score=score,
        )

        return await self.repository.create(new_owner)

    async def get_landlord(self, landlord_id: int) -> Optional[Owner]:
        return await self.repository.get_by_id(landlord_id)

    async def list_landlords(self) -> List[Owner]:
        return await self.repository.get_all()

    async def update_landlord(self, landlord_id: int, data: dict) -> Optional[Owner]:
        if "score" in data:
            data["score"] = max(0.0, min(float(data["score"]), 5.0))
            
        landlord = await self.repository.get_by_id(landlord_id)
        if not landlord:
            raise ValueError("Арендодатель не найден")

        reverify_required = False

        if "name" in data and data["name"] != landlord.name:
            reverify_required = True

        if "phone_numbers" in data and set(data["phone_numbers"]) != set(landlord.phone_numbers):
            reverify_required = True

        if "emails" in data and set(data["emails"]) != set(landlord.emails):
            reverify_required = True

        updated_landlord = await self.repository.update(landlord_id, data)

        return {
            "landlord": updated_landlord,
            "reverify_required": reverify_required #или добавить пользователям поле что они верифицированы
        }

    async def delete_landlord(self, landlord_id: int, session) -> bool:
        """
        Удаляет арендодателя, если у него нет активных броней.
        """
        landlord = await self.repository.get_by_id(landlord_id)
        if not landlord:
            raise ValueError("Арендодатель не найден")

        for equipment_id in landlord.equipment_list:
            active_bookings = await self.booking_repo.get_by_equipment(session, equipment_id)
            if active_bookings:
                raise ValueError(
                    f"Нельзя удалить арендодателя — у оборудования ID={equipment_id} есть активные бронирования"
                )

        return await self.repository.delete(landlord_id)
