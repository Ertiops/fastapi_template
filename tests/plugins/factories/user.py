from collections.abc import Callable
from datetime import datetime

import pytest
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.tables import UserTable
from tests.utils import IterUse, now_utc


class UserTableFactory(SQLAlchemyFactory[UserTable]):
    email = IterUse[str](lambda count: f"test{count}@test.com")
    username = IterUse[str](lambda count: f"test_username{count}")

    @classmethod
    def created_at(cls) -> datetime:
        return now_utc()

    @classmethod
    def updated_at(cls) -> datetime:
        return now_utc()

    @classmethod
    def deleted_at(cls) -> None:
        return None


@pytest.fixture
def create_user(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> UserTable:
        user: UserTable = UserTableFactory.build(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    return _factory
