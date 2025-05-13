import pytest

from app.domains.interfaces.storages.movie import IMovieStorage
from app.domains.interfaces.storages.user import IUserStorage
from app.domains.services.movie import MovieService
from app.domains.services.user import UserService


@pytest.fixture
def movie_service(movie_storage: IMovieStorage) -> MovieService:
    return MovieService(movie_storage=movie_storage)


@pytest.fixture
def user_service(user_storage: IUserStorage) -> UserService:
    return UserService(user_storage=user_storage)
