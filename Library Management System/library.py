from datetime import date


class Member:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.total_dues_amt = 0
        self.joined_date = date.today()
        self.borrowed_book = {}


class Book:
    def __init__(self, title, author, ISBN, stocks):
        self.title = title
        self.author = author
        self.ISBN = ISBN
        self.stocks = stocks
        self.is_available = True

    def __str__(self):
        return f"\nTitle: {self.title}\nAuthor: {self.author}\nISBN: {self.ISBN}\nStocks: {self.stocks}\n"


class Library:
    def __init__(self):
        self.fine_amt = 5
        self.books = {}
        self.borrowed_books_by_members = {}
        self.current_members = {}

    def add_books_stock(self, book_title, author, ISBN, stocks):
        try:
            if stocks is None or not isinstance(stocks, int) or stocks < 0:
                print("Stocks must be a non-negative integer!")
                return

            if ISBN in self.books:
                print("Book already exists!")
                return

            fields = {
                "book_title": book_title,
                "author": author,
                "ISBN": ISBN,
            }

            for field_name, value in fields.items():
                if value is None or not str(value).strip():
                    print(f"{field_name} cannot be empty or blank!")
                    return

            new_book = Book(book_title, author, ISBN, stocks)
            self.books[ISBN] = new_book

            print(self.books[ISBN])

        except Exception as e:
            print(e)

    def add_new_member(self, memeber_name, email):
        if email in self.current_members:
            print(f"{email} already exists!")
            return

        member = Member(memeber_name, email)
        self.current_members[email] = member
        print(f"{memeber_name} with {email} added successfully!\n")

    def borrow_books(self, email, *isbn_list):
        # 1. Check member exists
        if email not in self.current_members:
            print(f"Member with {email} doesn't exists!")
            return
        member = self.current_members[email]
        # 2. Check book exists
        for ISBN in isbn_list:
            if ISBN not in self.books:
                print(f"Book with ISBN {ISBN} not found.")
                continue

            # 3. Check stock
            book = self.books[ISBN]
            if book.stocks <= 0:
                print(f"{book.title} is out of stock!")
                continue
            # 4. Lend it
            book.stocks -= 1
            if book.stocks == 0:
                book.is_available = False

            member.borrowed_book[ISBN] = {"borrowed_date": date.today()}
            print(f"'{book.title}' borrowed successfully by {member.name}.")


def return_borrowed_books(self, email, isbn_list):
    # 1. Check member exists
    if email not in self.current_members:
        print(f"{email} Member doesn't exist!")
        return

    member = self.current_members[email]

    for isbn in isbn_list:
        # 2. Check if member borrowed this book
        if isbn not in member.borrowed_book:
            print(f"{isbn} not borrowed by {member.name}")
            continue

        # 3. Calculate days
        borrowed_date = member.borrowed_book[isbn]["borrowed_date"]
        total_days = (date.today() - borrowed_date).days

        # 4. Calculate fine
        fine_amt = 0
        if total_days > 14:
            fine_amt = (total_days - 14) * self.fine_amt

        member.total_dues_amt += fine_amt

        # 5. Update book stock
        book = self.books[isbn]
        book.stocks += 1
        book.is_available = True

        # 6. Remove from borrowed list
        del member.borrowed_book[isbn]

        print(f"{book.title} returned by {member.name}. Fine: Rs {fine_amt}")


lib = Library()
lib.add_books_stock("ram story", "ram", "12345B", 20)
lib.add_books_stock("The sun", "nischal", "12345C", 10)


lib.add_new_member("Nischal Shrestha", "snischal@gmail.com")
lib.add_new_member("Murti Thapa", "murti@gmail.com")

lib.borrow_books("snischal@gmail.com", "12345C", "12345B")
