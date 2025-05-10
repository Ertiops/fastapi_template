from app.adapters.database.tables import BookTable
from app.domains.entities.book import Book


def convert_book_table_to_dto(
    *,
    result: BookTable,
) -> Book:
    return Book(
        id=result.id,
        title=result.title,
        year=result.year,
        author=result.author,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
