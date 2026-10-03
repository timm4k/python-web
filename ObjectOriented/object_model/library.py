import math


class Book:
    def __init__(self, title: str, author: str, pages: int, price: float) -> None:
        normalized_title = title.strip()
        normalized_author = author.strip()
        if not normalized_title or not normalized_author:
            raise ValueError("Title and author are required")
        if pages < 1:
            raise ValueError("Pages must be positive")
        if not math.isfinite(price) or price < 0:
            raise ValueError("Price must be a finite non-negative number")
        self.title = normalized_title
        self.author = normalized_author
        self.pages = pages
        self.price = float(price)

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, author={self.author!r}, price={self.price})"

    def apply_discount(self, percent: float) -> None:
        if not math.isfinite(percent) or not 0 <= percent <= 100:
            raise ValueError("Discount must be between 0 and 100")
        self.price = round(self.price * (1 - percent / 100), 2)


def create_sample_books() -> tuple[Book, Book, Book]:
    return (
        Book("The Secret Ways of Perfume", "Cristina Caboni", 448, 520),
        Book("Perfume", "Patrick Suskind", 272, 390),
        Book("The Book of Scented Things", "Lila Moss", 316, 460),
    )


def main() -> None:
    books = create_sample_books()
    for book in books:
        print(book)
    books[1].apply_discount(15)
    print(f"After 15% discount: {books[1]}")


if __name__ == "__main__":
    main()
