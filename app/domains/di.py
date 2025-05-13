from dishka import Provider, Scope, provide

from app.domains.interfaces.storages.movie import IMovieStorage
from app.domains.interfaces.storages.user import IUserStorage
from app.domains.services.movie import MovieService
from app.domains.services.user import UserService


class DomainProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def movie_service(self, movie_storage: IMovieStorage) -> MovieService:
        return MovieService(movie_storage=movie_storage)

    @provide(scope=Scope.REQUEST)
    def user_service(self, user_storage: IUserStorage) -> UserService:
        return UserService(user_storage=user_storage)
