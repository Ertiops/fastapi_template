from collections.abc import Awaitable, Callable
from datetime import datetime

import pytest
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.tables import MovieTable
from tests.utils import now_utc


class MovieTableFactory(SQLAlchemyFactory[MovieTable]):
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
def create_movie(session: AsyncSession) -> Callable[..., Awaitable[MovieTable]]:
    async def _factory(**kwargs) -> MovieTable:
        movie: MovieTable = MovieTableFactory.build(**kwargs)
        session.add(movie)
        await session.commit()
        await session.refresh(movie)
        return movie

    return _factory
