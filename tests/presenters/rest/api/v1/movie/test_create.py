from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import MovieTable
from app.domains.entities.movie import MovieGenre
from tests.utils import now_utc

API_URL = "/api/v1/movies/"


@pytest.mark.parametrize(
    "json_data",
    (
        dict(title="t" * 2),
        dict(title="t" * 256),
        dict(year=0),
        dict(year=now_utc().year + 1),
        dict(director="t" * 2),
        dict(director="t" * 256),
        dict(genre="test_wrong_genre"),
        dict(duration_minutes=0),
        dict(rating=0),
        dict(rating=11),
    ),
)
async def test__create__unprocessable_entity(
    client: AsyncClient,
    json_data: Mapping[str, Any],
) -> None:
    response = await client.post(API_URL, json=json_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__create__ok__status(client: AsyncClient) -> None:
    response = await client.post(
        API_URL,
        json=dict(
            title="test_book",
            description="test_description",
            year=now_utc().year,
            director="test_director",
            genre=MovieGenre.COMEDY,
            duration_minutes=100,
            rating=4.5,
        ),
    )
    assert response.status_code == HTTPStatus.CREATED


async def test__create__ok__format(client: AsyncClient) -> None:
    json_data = dict(
        title="test_book",
        description="test_description",
        year=now_utc().year,
        director="test_director",
        genre=MovieGenre.COMEDY,
        duration_minutes=100,
        rating=4.5,
    )
    response = await client.post(API_URL, json=json_data)
    assert response.json() == dict(
        id=IsStr,
        title=json_data.get("title"),
        description=json_data.get("description"),
        year=json_data.get("year"),
        director=json_data.get("director"),
        genre=json_data.get("genre"),
        duration_minutes=json_data.get("duration_minutes"),
        rating=json_data.get("rating"),
        created_at=IsStr,
        updated_at=IsStr,
    )


async def test__create__duplicate__conflict(
    client: AsyncClient,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie(year=now_utc().year)
    response = await client.post(
        API_URL,
        json=dict(
            title=db_movie.title,
            description="test_description",
            year=db_movie.year,
            director=db_movie.director,
            genre=MovieGenre.COMEDY,
            duration_minutes=120,
            rating=4.5,
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT
