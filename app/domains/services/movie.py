from uuid import UUID

from app.application.exceptions import EntityNotFoundException
from app.domains.entities.movie import (
    CreateMovie,
    Movie,
    MovieList,
    MovieListParams,
    UpdateMovie,
)
from app.domains.interfaces.storages.movie import IMovieStorage


class MovieService:
    __movie_storage: IMovieStorage

    def __init__(self, movie_storage: IMovieStorage) -> None:
        self.__movie_storage = movie_storage

    async def create(self, *, input_dto: CreateMovie) -> Movie:
        return await self.__movie_storage.create(input_dto=input_dto)

    async def get_by_id(self, *, input_id: UUID) -> Movie:
        book = await self.__movie_storage.get_by_id(input_id=input_id)
        if book is None:
            raise EntityNotFoundException(entity=Movie, entity_id=input_id)
        return book

    async def get_list(self, *, input_dto: MovieListParams) -> MovieList:
        total = await self.__movie_storage.count(input_dto=input_dto)
        items = await self.__movie_storage.get_list(input_dto=input_dto)
        return MovieList(total=total, items=items)

    async def update_by_id(self, *, input_dto: UpdateMovie) -> Movie:
        if not await self.__movie_storage.exists_by_id(input_id=input_dto.id):
            raise EntityNotFoundException(entity=Movie, entity_id=input_dto.id)
        return await self.__movie_storage.update_by_id(input_dto=input_dto)

    async def delete_by_id(self, *, input_id: UUID) -> None:
        if not await self.__movie_storage.exists_by_id(input_id=input_id):
            raise EntityNotFoundException(entity=Movie, entity_id=input_id)
        await self.__movie_storage.delete_by_id(input_id=input_id)
