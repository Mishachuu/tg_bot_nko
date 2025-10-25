from app.repositories.category_repository import CategoryRepository
from sqlalchemy.ext.asyncio import AsyncSession

class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self._repo = repo

    async def seed_categories(self, session: AsyncSession, categories: list[str]):
        for name in categories:
            try:
                await self._repo.create(session, name)
            except Exception:
                pass
        await session.commit()

    async def list_categories(self, session: AsyncSession):
        return await self._repo.get_all(session)
