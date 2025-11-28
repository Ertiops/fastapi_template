from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import MovieTable
from app.domain.entities.movie import MovieGenre
from tests.utils import now_utc


def api_url(movie_id: UUID = uuid4()) -> str:
    return f"/api/v1/movies/{movie_id}/"


@pytest.mark.parametrize(
    "json_data",
    (
        dict(title="t" * 2),
        dict(title="t" * 256),
        dict(year=now_utc().year + 1),
        dict(director="t" * 2),
        dict(director="t" * 256),
        dict(genre="test_wrong_genre"),
        dict(rating=11),
    ),
)
async def test__update_by_id__unprocessable_entity(
    client: AsyncClient, json_data: Mapping[str, Any]
) -> None:
    response = await client.patch(api_url(), json=json_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__update_by_id__unprocessable_entity__empty_payload(
    client: AsyncClient,
) -> None:
    response = await client.patch(api_url())
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__update_by_id__not_found(client: AsyncClient) -> None:
    response = await client.patch(
        api_url(),
        json=dict(title="test_movie"),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test__update_by_id__ok__status(
    client: AsyncClient,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    response = await client.patch(
        api_url(db_movie.id),
        json=dict(title="test_movie"),
    )
    assert response.status_code == HTTPStatus.OK


async def test__update_by_id__ok__format(
    client: AsyncClient,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    json_data = dict(
        title="test_title",
        description="test_description",
        year=now_utc().year,
        director="test_director",
        genre=MovieGenre.COMEDY,
        duration_minutes=100,
        rating=4.5,
    )
    response = await client.patch(api_url(db_movie.id), json=json_data)
    assert response.json() == dict(
        id=str(db_movie.id),
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


async def test__update_by_id__conflict__duplicate(
    client: AsyncClient,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie(year=now_utc().year)
    db_movie_to_update: MovieTable = await create_movie()
    response = await client.patch(
        api_url(db_movie_to_update.id),
        json=dict(
            title=db_movie.title,
            year=db_movie.year,
            director=db_movie.director,
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT
