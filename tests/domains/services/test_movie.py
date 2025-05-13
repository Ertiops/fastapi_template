from collections.abc import Callable
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsDatetime, IsUUID

from app.adapters.database.tables import MovieTable
from app.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domains.entities.movie import (
    CreateMovie,
    Movie,
    MovieGenre,
    MovieList,
    MovieListParams,
    UpdateMovie,
)
from app.domains.services.movie import MovieService
from tests.utils import now_utc


async def test__create(movie_service: MovieService) -> None:
    create_data = CreateMovie(
        title="test_title",
        description="test_description",
        year=now_utc().year,
        director="test_director",
        genre=MovieGenre.COMEDY,
        duration_minutes=120,
        rating=4.5,
    )
    movie = await movie_service.create(input_dto=create_data)
    assert movie == Movie(
        id=IsUUID,
        title=create_data.title,
        description=create_data.description,
        year=create_data.year,
        director=create_data.director,
        genre=create_data.genre,
        duration_minutes=create_data.duration_minutes,
        rating=create_data.rating,
        created_at=IsDatetime,
        updated_at=IsDatetime,
    )


async def test__get_by_id(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    movie = await movie_service.get_by_id(input_id=db_movie.id)
    assert movie == Movie(
        id=db_movie.id,
        title=db_movie.title,
        description=db_movie.description,
        year=db_movie.year,
        director=db_movie.director,
        genre=db_movie.genre,
        duration_minutes=db_movie.duration_minutes,
        rating=db_movie.rating,
        created_at=db_movie.created_at,
        updated_at=db_movie.updated_at,
    )


async def test__get_by_id__entity_not_found_exception(
    movie_service: MovieService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await movie_service.get_by_id(input_id=uuid4())


async def test__get_list(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movies: list[MovieTable] = [
        await create_movie(id=UUID(int=i + 1)) for i in range(2)
    ]
    movies = await movie_service.get_list(input_dto=MovieListParams(limit=10, offset=0))
    assert movies == MovieList(
        total=len(db_movies),
        items=[
            Movie(
                id=db_movie.id,
                title=db_movie.title,
                description=db_movie.description,
                year=db_movie.year,
                director=db_movie.director,
                genre=db_movie.genre,
                duration_minutes=db_movie.duration_minutes,
                rating=db_movie.rating,
                created_at=db_movie.created_at,
                updated_at=db_movie.updated_at,
            )
            for db_movie in db_movies
        ],
    )


async def test__get_list__validate_limit(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movies: list[MovieTable] = [
        await create_movie(id=UUID(int=i + 1)) for i in range(2)
    ]
    movies = await movie_service.get_list(input_dto=MovieListParams(limit=1, offset=0))
    assert movies == MovieList(
        total=len(db_movies),
        items=[
            Movie(
                id=db_movie.id,
                title=db_movie.title,
                description=db_movie.description,
                year=db_movie.year,
                director=db_movie.director,
                genre=db_movie.genre,
                duration_minutes=db_movie.duration_minutes,
                rating=db_movie.rating,
                created_at=db_movie.created_at,
                updated_at=db_movie.updated_at,
            )
            for db_movie in db_movies
        ][:1],
    )


async def test__get_list__validate_offset(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movies: list[MovieTable] = [
        await create_movie(id=UUID(int=i + 1)) for i in range(2)
    ]
    movies = await movie_service.get_list(input_dto=MovieListParams(limit=2, offset=1))
    assert movies == MovieList(
        total=len(db_movies),
        items=[
            Movie(
                id=db_movie.id,
                title=db_movie.title,
                description=db_movie.description,
                year=db_movie.year,
                director=db_movie.director,
                genre=db_movie.genre,
                duration_minutes=db_movie.duration_minutes,
                rating=db_movie.rating,
                created_at=db_movie.created_at,
                updated_at=db_movie.updated_at,
            )
            for db_movie in db_movies
        ][1:],
    )


async def test__get_list__empty_list(movie_service: MovieService) -> None:
    movies = await movie_service.get_list(input_dto=MovieListParams(limit=2, offset=1))
    assert movies == MovieList(total=0, items=[])


async def test__update_by_id(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    update_data = UpdateMovie(
        id=db_movie.id,
        title="test_title",
        description="test_description",
        year=now_utc().year,
        director="test_director",
        genre=MovieGenre.COMEDY,
        duration_minutes=100,
        rating=4.5,
    )
    movie = await movie_service.update_by_id(input_dto=update_data)
    assert movie == Movie(
        id=db_movie.id,
        title=update_data.title,
        description=update_data.description,
        year=update_data.year,
        director=update_data.director,
        genre=update_data.genre,
        duration_minutes=update_data.duration_minutes,
        rating=update_data.rating,
        created_at=db_movie.created_at,
        updated_at=IsDatetime,
    )


async def test__update_by_id__entity_not_found_exception(
    movie_service: MovieService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await movie_service.update_by_id(
            input_dto=UpdateMovie(
                id=uuid4(),
                title="test_title",
            )
        )


async def test__update_by_id__entity_already_exists_exception(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    db_movie_to_update: MovieTable = await create_movie()
    with pytest.raises(EntityAlreadyExistsException):
        await movie_service.update_by_id(
            input_dto=UpdateMovie(
                id=db_movie_to_update.id,
                title=db_movie.title,
                year=db_movie.year,
                director=db_movie.director,
            )
        )


async def test__delete_by_id(
    movie_service: MovieService,
    create_movie: Callable,
) -> None:
    db_movie: MovieTable = await create_movie()
    await movie_service.delete_by_id(input_id=db_movie.id)
    assert db_movie.deleted_at is not None


async def test__delete_by_id__entity_not_found_exception(
    movie_service: MovieService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await movie_service.delete_by_id(input_id=uuid4())
