import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.storages.book import BookStorage
from app.adapters.database.storages.user import UserStorage
from app.domains.interfaces.storages.book import IBookStorage
from app.domains.interfaces.storages.user import IUserStorage


@pytest.fixture
def book_storage(session: AsyncSession) -> IBookStorage:
    return BookStorage(session=session)


@pytest.fixture
def user_storage(session: AsyncSession) -> IUserStorage:
    return UserStorage(session=session)
