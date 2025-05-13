from collections.abc import Callable

import pytest
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.tables import MovieTable


class MovieTableFactory(SQLAlchemyFactory[MovieTable]):
    @classmethod
    def deleted_at(cls) -> None:
        return None


@pytest.fixture
def create_movie(session: AsyncSession) -> Callable:
    async def _factory(**kwargs) -> MovieTable:
        movie = MovieTableFactory.build(**kwargs)
        session.add(movie)
        await session.commit()
        await session.refresh(movie)
        return movie

    return _factory
