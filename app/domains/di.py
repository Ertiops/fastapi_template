from dishka import Provider, Scope, provide

from app.domains.interfaces.storages.book import IBookStorage
from app.domains.interfaces.storages.user import IUserStorage
from app.domains.services.book import BookService
from app.domains.services.user import UserService


class DomainProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def book_service(self, book_storage: IBookStorage) -> BookService:
        return BookService(book_storage=book_storage)

    @provide(scope=Scope.REQUEST)
    def user_service(self, user_storage: IUserStorage) -> UserService:
        return UserService(user_storage=user_storage)
