import pytest

from app.domain.interfaces.storages.movie import IMovieStorage
from app.domain.services.movie import MovieService


@pytest.fixture
def movie_service(movie_storage: IMovieStorage) -> MovieService:
    return MovieService(movie_storage=movie_storage)
