import pytest

from app.domains.interfaces.storages.book import IBookStorage
from app.domains.interfaces.storages.user import IUserStorage
from app.domains.services.book import BookService
from app.domains.services.user import UserService


@pytest.fixture
def book_service(book_storage: IBookStorage) -> BookService:
    return BookService(book_storage=book_storage)


@pytest.fixture
def user_service(user_storage: IUserStorage) -> UserService:
    return UserService(user_storage=user_storage)
