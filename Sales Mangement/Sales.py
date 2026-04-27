"""
Sales Management System
-----------------------
A CLI-based application for managing products, customers, and sales transactions.

Modules used:
    abc       - Abstract base class enforcement
    functools - reduce() for revenue aggregation
    datetime  - Timestamping sale records
"""

from abc import ABC, abstractmethod
from functools import reduce
import datetime


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class Catalog(ABC):
    """
    Abstract interface for any product catalog implementation.

    Subclasses must provide concrete implementations of display_all()
    and search() to ensure a consistent browsing contract regardless
    of the underlying storage mechanism.
    """

    @abstractmethod
    def display_all(self):
        """Render all catalog entries to stdout."""
        pass

    @abstractmethod
    def search(self, keyword: str):
        """Return entries matching the given keyword."""
        pass


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class Product:
    """
    Represents a sellable product with controlled access to its price and stock.

    Price and stock are kept private to prevent invalid assignments
    (e.g., negative values) from bypassing validation logic.

    Args:
        product_id (str):   Unique identifier for the product.
        name       (str):   Display name.
        price      (float): Unit selling price in Rs.
        category   (str):   Grouping label (e.g., "Electronics").
        stock      (int):   Available quantity.
    """

    def __init__(
        self, product_id: str, name: str, price: float, category: str, stock: int
    ):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.__price = price
        self.__stock = stock

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float):
        if value < 0:
            print("  [!] Price cannot be negative.")
        else:
            self.__price = value

    @property
    def stock(self) -> int:
        return self.__stock

    @stock.setter
    def stock(self, value: int):
        if value < 0:
            print("  [!] Stock cannot go below 0.")
        else:
            self.__stock = value

    def __str__(self) -> str:
        return (
            f"[{self.product_id}] {self.name:<20} | "
            f"Rs.{self.__price:>8.2f} | "
            f"Category: {self.category:<12} | "
            f"Stock: {self.__stock}"
        )


class Customer:
    """
    Stores customer profile data and a chronological record of their sale IDs.

    purchase_history retains insertion order and allows duplicates,
    which is necessary for customers who buy the same product multiple times.

    Args:
        customer_id (str): Unique identifier for the customer.
        name        (str): Full name.
        phone       (str): Contact number.
    """

    def __init__(self, customer_id: str, name: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.purchase_history = []

    def add_purchase(self, sale_id: str):
        """Append a completed sale ID to this customer's history."""
        self.purchase_history.append(sale_id)

    def __str__(self) -> str:
        return (
            f"[{self.customer_id}] {self.name:<20} | "
            f"Phone: {self.phone} | "
            f"Purchases: {len(self.purchase_history)}"
        )


class SaleRecord:
    """
    Immutable record of a single sales transaction.

    Core transaction data is stored in a tuple to prevent accidental
    mutation after the sale is confirmed. Derived fields such as totals
    are computed at construction time and exposed via properties.

    A discount function may be injected at creation time, allowing
    the caller to apply any pricing strategy without modifying this class.

    Args:
        customer_id  (str):      ID of the purchasing customer.
        product_id   (str):      ID of the product sold.
        product_name (str):      Name of the product at time of sale.
        qty          (int):      Units sold.
        unit_price   (float):    Original unit price before discount.
        discount_fn  (callable): Optional function that accepts a price
                                 and returns the discounted price.
    """

    _id_counter = 1000  # Shared counter; incremented before each new sale ID

    def __init__(
        self,
        customer_id: str,
        product_id: str,
        product_name: str,
        qty: int,
        unit_price: float,
        discount_fn=None,
    ):

        SaleRecord._id_counter += 1
        self.sale_id = f"S{SaleRecord._id_counter}"
        self.customer_id = customer_id
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        final_price = discount_fn(unit_price) if discount_fn else unit_price

        # Immutable snapshot: (sale_id, product_id, name, qty, original_price, final_price)
        self.snapshot = (
            self.sale_id,
            product_id,
            product_name,
            qty,
            unit_price,
            final_price,
        )
        self.total = final_price * qty

    @property
    def product_id(self) -> str:
        return self.snapshot[1]

    @property
    def product_name(self) -> str:
        return self.snapshot[2]

    @property
    def qty(self) -> int:
        return self.snapshot[3]

    @property
    def unit_price(self) -> float:
        return self.snapshot[4]

    @property
    def final_unit_price(self) -> float:
        return self.snapshot[5]

    def __str__(self) -> str:
        discount_note = ""
        if self.unit_price != self.final_unit_price:
            discount_note = f" [Discounted from Rs.{self.unit_price:.2f}]"
        return (
            f"{self.sale_id} | {self.timestamp} | "
            f"Customer: {self.customer_id} | "
            f"{self.product_name} x{self.qty} | "
            f"Unit: Rs.{self.final_unit_price:.2f}{discount_note} | "
            f"Total: Rs.{self.total:.2f}"
        )


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


class Inventory(Catalog):
    """
    Concrete implementation of Catalog that stores products in a dictionary.

    Using a dict keyed by product_id gives O(1) lookups during high-frequency
    operations such as stock checks at sale time.

    Inherits from Catalog and provides implementations for display_all()
    and search() as required by the abstract contract.
    """

    def __init__(self):
        self.__products = {}

    def add_product(self, product: Product):
        """
        Register a new product in the inventory.

        Rejects duplicate product IDs to maintain data integrity.
        """
        if product.product_id in self.__products:
            print(f"  [!] Product ID '{product.product_id}' already exists.")
        else:
            self.__products[product.product_id] = product
            print(f"  [+] '{product.name}' added to inventory.")

    def get_product(self, product_id: str):
        """Return the Product for the given ID, or None if not found."""
        return self.__products.get(product_id, None)

    def all_products(self) -> list:
        """Return a list of all registered Product objects."""
        return list(self.__products.values())

    def display_all(self):
        """Print a formatted table of all products."""
        if not self.__products:
            print("  No products in inventory.")
            return
        print(f"\n  {'─'*75}")
        print(f"  {'ID':<8} {'Name':<20} {'Price':>10} {'Category':<14} {'Stock':>6}")
        print(f"  {'─'*75}")
        for p in self.__products.values():
            print(f"  {p}")
        print(f"  {'─'*75}\n")

    def search(self, keyword: str) -> list:
        """
        Return products whose name or category contains the keyword.

        The search is case-insensitive to accommodate varied user input.
        """
        keyword = keyword.lower()
        return [
            p
            for p in self.__products.values()
            if keyword in p.name.lower() or keyword in p.category.lower()
        ]

    def low_stock_alert(self, threshold: int = 5) -> list:
        """Return products with stock below the given threshold."""
        return [p for p in self.__products.values() if p.stock < threshold]

    def get_all_categories(self) -> set:
        """Return the set of distinct category names across all products."""
        return set(p.category for p in self.__products.values())


# ---------------------------------------------------------------------------
# Sales manager
# ---------------------------------------------------------------------------


class SalesManager:
    """
    Central controller that orchestrates products, customers, and transactions.

    Discount strategies are stored as a class-level dict of lambdas so they
    remain accessible without instantiation and can be referenced by key
    both internally and from the CLI layer.
    """

    DISCOUNTS = {
        "none": lambda p: p,
        "10%": lambda p: round(p * 0.90, 2),
        "20%": lambda p: round(p * 0.80, 2),
        "festival": lambda p: round(
            p * 0.85, 2
        ),  # 15% seasonal discount (Dashain/Tihar)
    }

    def __init__(self):
        self.inventory = Inventory()
        self.__customers = {}
        self.__sales = []

    # --- Customer operations ---

    def register_customer(self, customer_id: str, name: str, phone: str):
        """Add a new customer to the registry, rejecting duplicate IDs."""
        if customer_id in self.__customers:
            print(f"  [!] Customer ID '{customer_id}' already registered.")
        else:
            self.__customers[customer_id] = Customer(customer_id, name, phone)
            print(f"  [+] Customer '{name}' registered.")

    def get_customer(self, customer_id: str):
        """Return the Customer for the given ID, or None if not found."""
        return self.__customers.get(customer_id, None)

    def display_customers(self):
        """Print a summary of all registered customers."""
        if not self.__customers:
            print("  No customers registered yet.")
            return
        print(f"\n  {'─'*65}")
        for c in self.__customers.values():
            print(f"  {c}")
        print(f"  {'─'*65}\n")

    # --- Sales operations ---

    def make_sale(
        self, customer_id: str, product_id: str, qty: int, discount_key: str = "none"
    ):
        """
        Process a sale transaction.

        Validates customer existence, product availability, and stock
        before committing. On success, deducts stock, appends the
        SaleRecord to the sales ledger, and links it to the customer's
        purchase history.

        Args:
            customer_id  (str): ID of the purchasing customer.
            product_id   (str): ID of the product being sold.
            qty          (int): Quantity to sell.
            discount_key (str): Key from DISCOUNTS to apply (default: "none").
        """
        customer = self.get_customer(customer_id)
        if not customer:
            print(f"  [!] Customer '{customer_id}' not found.")
            return

        product = self.inventory.get_product(product_id)
        if not product:
            print(f"  [!] Product '{product_id}' not found.")
            return

        if product.stock < qty:
            print(f"  [!] Insufficient stock. Available: {product.stock}")
            return

        discount_fn = self.DISCOUNTS.get(discount_key, self.DISCOUNTS["none"])

        sale = SaleRecord(
            customer_id=customer_id,
            product_id=product_id,
            product_name=product.name,
            qty=qty,
            unit_price=product.price,
            discount_fn=discount_fn,
        )

        product.stock = product.stock - qty
        self.__sales.append(sale)
        customer.add_purchase(sale.sale_id)

        print(f"\n  Sale recorded successfully.")
        print(f"  {sale}\n")

    # --- Analytics ---

    def total_revenue(self) -> float:
        """Return the cumulative revenue across all recorded sales."""
        if not self.__sales:
            return 0.0
        return reduce(lambda acc, sale: acc + sale.total, self.__sales, 0.0)

    def sales_report(self):
        """Print a full ledger of all transactions with a revenue summary."""
        if not self.__sales:
            print("  No sales recorded yet.")
            return

        print(f"\n  {'─'*85}")
        print("   SALES REPORT")
        print(f"  {'─'*85}")

        for line in map(lambda s: f"  {s}", self.__sales):
            print(line)

        print(f"  {'─'*85}")
        print(f"  TOTAL REVENUE : Rs.{self.total_revenue():,.2f}")
        print(f"  TOTAL SALES   : {len(self.__sales)}")
        print(f"  {'─'*85}\n")

    def revenue_by_category(self) -> dict:
        """
        Compute total revenue broken down by product category.

        For each category, filters the sales ledger to matching transactions
        and reduces them to a single revenue figure.

        Returns:
            dict mapping category name to total revenue. Categories with
            no sales are excluded from the result.
        """
        report = {}
        for cat in self.inventory.get_all_categories():
            cat_sales = list(
                filter(
                    lambda s: (
                        self.inventory.get_product(s.product_id) is not None
                        and self.inventory.get_product(s.product_id).category == cat
                    ),
                    self.__sales,
                )
            )
            if cat_sales:
                report[cat] = reduce(lambda acc, s: acc + s.total, cat_sales, 0.0)
        return report

    def top_products(self, n: int = 3) -> list:
        """
        Return the top N products ranked by total revenue generated.

        Aggregates per-product revenue and quantity from the sales ledger,
        then sorts descending by revenue.

        Args:
            n (int): Number of top products to return.

        Returns:
            List of (product_id, {"name": str, "revenue": float, "qty": int})
            tuples, sorted by revenue descending.
        """
        revenue_map = {}
        for sale in self.__sales:
            if sale.product_id not in revenue_map:
                revenue_map[sale.product_id] = {
                    "name": sale.product_name,
                    "revenue": 0.0,
                    "qty": 0,
                }
            revenue_map[sale.product_id]["revenue"] += sale.total
            revenue_map[sale.product_id]["qty"] += sale.qty

        sorted_products = sorted(
            revenue_map.items(), key=lambda item: item[1]["revenue"], reverse=True
        )
        return sorted_products[:n]

    def unique_buyers_today(self) -> set:
        """
        Return the set of customer IDs who completed a purchase today.

        Using a set ensures each customer is counted once regardless
        of how many transactions they made during the day.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return {s.customer_id for s in self.__sales if s.timestamp.startswith(today)}

    def customer_history(self, customer_id: str):
        """
        Print all transactions for the specified customer along with
        their cumulative spend.
        """
        customer = self.get_customer(customer_id)
        if not customer:
            print("  [!] Customer not found.")
            return

        print(f"\n  Purchase history for {customer.name}:")
        print(f"  {'─'*85}")

        cust_sales = list(filter(lambda s: s.customer_id == customer_id, self.__sales))

        if not cust_sales:
            print("  No purchases recorded.")
        else:
            for s in cust_sales:
                print(f"  {s}")
            total_spent = reduce(lambda acc, s: acc + s.total, cust_sales, 0.0)
            print(f"  {'─'*85}")
            print(f"  Total Spent: Rs.{total_spent:,.2f}\n")

    def low_stock_report(self, threshold: int = 5):
        """Print all products whose stock has fallen below the given threshold."""
        alerts = self.inventory.low_stock_alert(threshold)
        if not alerts:
            print(f"  All products have stock above {threshold}.")
        else:
            print(f"\n  Low Stock Alert  (threshold: {threshold})")
            print(f"  {'─'*50}")
            for p in alerts:
                print(f"  {p}")
            print(f"  {'─'*50}\n")


# ---------------------------------------------------------------------------
# CLI utilities
# ---------------------------------------------------------------------------


def print_header(title: str):
    """Render a section header to stdout."""
    print(f"\n  {'═'*60}")
    print(f"   {title}")
    print(f"  {'═'*60}")


def get_int_input(prompt: str, min_val: int = 1) -> int:
    """
    Prompt the user for an integer and repeat until a valid value is entered.

    Args:
        prompt  (str): Text displayed to the user.
        min_val (int): Minimum acceptable value (inclusive).

    Returns:
        A validated integer >= min_val.
    """
    while True:
        try:
            val = int(input(prompt))
            if val < min_val:
                print(f"  [!] Value must be at least {min_val}.")
            else:
                return val
        except ValueError:
            print("  [!] Please enter a valid integer.")


def seed_demo_data(manager: SalesManager):
    """
    Populate the system with sample products, customers, and sales for
    immediate testing without manual data entry.

    Products are defined as a list of tuples and converted to Product
    objects via map() to keep the initialisation concise.
    """
    products = [
        ("P001", "Laptop Pro 15", 85000, "Electronics", 10),
        ("P002", "USB-C Hub", 2500, "Electronics", 50),
        ("P003", "Python Book", 1200, "Books", 30),
        ("P004", "Office Chair", 12000, "Furniture", 8),
        ("P005", "Standing Desk", 25000, "Furniture", 4),
        ("P006", "Notebook (Pack)", 350, "Stationery", 3),
        ("P007", "Wireless Mouse", 3500, "Electronics", 20),
        ("P008", "Data Science Book", 1500, "Books", 15),
    ]

    for p in map(lambda t: Product(t[0], t[1], t[2], t[3], t[4]), products):
        manager.inventory.add_product(p)

    customers = [
        ("C001", "Aarav Sharma", "9841000001"),
        ("C002", "Sita Thapa", "9852000002"),
        ("C003", "Bikash Karki", "9863000003"),
    ]
    for cid, name, phone in customers:
        manager.register_customer(cid, name, phone)

    manager.make_sale("C001", "P001", 1, "10%")
    manager.make_sale("C001", "P002", 2, "none")
    manager.make_sale("C002", "P003", 3, "festival")
    manager.make_sale("C003", "P007", 1, "20%")
    manager.make_sale("C002", "P004", 1, "none")

    print("\n  Demo data loaded.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    manager = SalesManager()

    print_header("SALES MANAGEMENT SYSTEM")
    print("  Loading demo data...")
    seed_demo_data(manager)

    while True:
        print(
            """
  ┌─────────────────────────────────────┐
  │         MAIN MENU                   │
  ├─────────────────────────────────────┤
  │  1.  View All Products              │
  │  2.  Add New Product                │
  │  3.  Search Products                │
  │  4.  Make a Sale                    │
  │  5.  Sales Report                   │
  │  6.  Revenue by Category            │
  │  7.  Top Products                   │
  │  8.  View All Customers             │
  │  9.  Customer Purchase History      │
  │  10. Low Stock Alert                │
  │  11. Unique Buyers Today            │
  │  12. Update Product Price           │
  │  0.  Exit                           │
  └─────────────────────────────────────┘"""
        )

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            print_header("ALL PRODUCTS")
            manager.inventory.display_all()

        elif choice == "2":
            print_header("ADD NEW PRODUCT")
            pid = input("  Product ID   : ").strip()
            name = input("  Name         : ").strip()
            price = float(input("  Price (Rs.)  : "))
            category = input("  Category     : ").strip()
            stock = get_int_input("  Stock qty    : ", min_val=0)
            manager.inventory.add_product(Product(pid, name, price, category, stock))

        elif choice == "3":
            print_header("SEARCH PRODUCTS")
            kw = input("  Enter keyword (name or category): ").strip()
            results = manager.inventory.search(kw)
            if not results:
                print("  No products matched.")
            else:
                for p in results:
                    print(f"  {p}")

        elif choice == "4":
            print_header("MAKE A SALE")
            cid = input("  Customer ID : ").strip()
            pid = input("  Product ID  : ").strip()
            qty = get_int_input("  Quantity    : ")
            print("  Discount options: none | 10% | 20% | festival")
            disc = input("  Discount key: ").strip().lower()
            if disc not in SalesManager.DISCOUNTS:
                print("  [!] Unrecognised discount key — applying 'none'.")
                disc = "none"
            manager.make_sale(cid, pid, qty, disc)

        elif choice == "5":
            print_header("SALES REPORT")
            manager.sales_report()

        elif choice == "6":
            print_header("REVENUE BY CATEGORY")
            report = manager.revenue_by_category()
            if not report:
                print("  No sales data yet.")
            else:
                print(f"  {'─'*40}")
                for cat, rev in sorted(
                    report.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"  {cat:<15} : Rs.{rev:>12,.2f}")
                print(f"  {'─'*40}")

        elif choice == "7":
            print_header("TOP PRODUCTS BY REVENUE")
            top = manager.top_products(n=5)
            if not top:
                print("  No sales yet.")
            else:
                print(f"  {'─'*55}")
                print(f"  {'Rank':<6} {'Product':<22} {'Qty Sold':>9} {'Revenue':>12}")
                print(f"  {'─'*55}")
                for rank, (pid, data) in enumerate(top, 1):
                    print(
                        f"  {rank:<6} {data['name']:<22} {data['qty']:>9} Rs.{data['revenue']:>10,.2f}"
                    )
                print(f"  {'─'*55}\n")

        elif choice == "8":
            print_header("ALL CUSTOMERS")
            manager.display_customers()

        elif choice == "9":
            print_header("CUSTOMER HISTORY")
            cid = input("  Enter Customer ID: ").strip()
            manager.customer_history(cid)

        elif choice == "10":
            print_header("LOW STOCK ALERT")
            manager.low_stock_report(threshold=5)

        elif choice == "11":
            print_header("UNIQUE BUYERS TODAY")
            buyers = manager.unique_buyers_today()
            if not buyers:
                print("  No sales recorded today.")
            else:
                print(f"  {len(buyers)} unique buyer(s) today: {', '.join(buyers)}\n")

        elif choice == "12":
            print_header("UPDATE PRODUCT PRICE")
            pid = input("  Product ID  : ").strip()
            product = manager.inventory.get_product(pid)
            if not product:
                print(f"  [!] Product '{pid}' not found.")
            else:
                print(f"  Current price: Rs.{product.price:.2f}")
                new_price = float(input("  New price (Rs.): "))
                product.price = new_price
                print(f"  [+] Price updated to Rs.{product.price:.2f}")

        elif choice == "0":
            print("\n  Goodbye!\n")
            break

        else:
            print("  [!] Invalid choice. Try again.")


if __name__ == "__main__":
    main()
