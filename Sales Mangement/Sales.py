# =============================================================================
#  SALES MANAGEMENT SYSTEM
#  Concepts: OOP (Encapsulation, Inheritance, Polymorphism, Abstraction)
#            dict, list, set, tuple, lambda, map, filter, reduce,
#            @property, @abstractmethod, __str__, list comprehension
# =============================================================================

from abc import ABC, abstractmethod  # OOP: Abstraction
from functools import reduce  # reduce()
import datetime

# =============================================================================
# SECTION 1 — ABSTRACT BASE CLASS  (OOP: Abstraction)
# =============================================================================


class Catalog(ABC):
    """
    Abstract base class. Any class that inherits this MUST implement
    `display_all()` and `search()` — like a contract on the wall.
    """

    @abstractmethod
    def display_all(self):
        pass

    @abstractmethod
    def search(self, keyword):
        pass


# =============================================================================
# SECTION 2 — PRODUCT CLASS  (OOP: Encapsulation, @property)
# =============================================================================


class Product:
    """
    Represents a single product.
    Private attributes accessed via @property and setters.
    """

    def __init__(self, product_id, name, price, category, stock):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.__price = price  # Encapsulation: private
        self.__stock = stock  # Encapsulation: private

    # --- @property: controlled read access ---
    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        if value < 0:
            print("  [!] Price cannot be negative.")
        else:
            self.__price = value

    @property
    def stock(self):
        return self.__stock

    @stock.setter
    def stock(self, value):
        if value < 0:
            print("  [!] Stock cannot go below 0.")
        else:
            self.__stock = value

    # OOP: Polymorphism — __str__ overridden
    def __str__(self):
        return (
            f"[{self.product_id}] {self.name:<20} | "
            f"Rs.{self.__price:>8.2f} | "
            f"Category: {self.category:<12} | "
            f"Stock: {self.__stock}"
        )


# =============================================================================
# SECTION 3 — CUSTOMER CLASS  (OOP: Encapsulation)
# =============================================================================


class Customer:
    """
    Stores customer info and a history of their sale IDs.
    Purchase history is a list — ordered, allows duplicates (repeat buys).
    """

    def __init__(self, customer_id, name, phone):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.purchase_history = []  # DATA STRUCTURE: list

    def add_purchase(self, sale_id):
        self.purchase_history.append(sale_id)

    def __str__(self):
        return (
            f"[{self.customer_id}] {self.name:<20} | "
            f"Phone: {self.phone} | "
            f"Purchases: {len(self.purchase_history)}"
        )


# =============================================================================
# SECTION 4 — SALE RECORD CLASS
# =============================================================================


class SaleRecord:
    """
    Immutable snapshot of one transaction.
    Core data stored as a tuple for read-only safety.
    """

    _id_counter = 1000  # class variable — shared across all instances

    def __init__(
        self, customer_id, product_id, product_name, qty, unit_price, discount_fn=None
    ):
        SaleRecord._id_counter += 1
        self.sale_id = f"S{SaleRecord._id_counter}"
        self.customer_id = customer_id
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Apply discount if a lambda/function was passed
        final_price = discount_fn(unit_price) if discount_fn else unit_price

        # DATA STRUCTURE: tuple — immutable sale snapshot
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
    def product_id(self):
        return self.snapshot[1]

    @property
    def product_name(self):
        return self.snapshot[2]

    @property
    def qty(self):
        return self.snapshot[3]

    @property
    def unit_price(self):
        return self.snapshot[4]

    @property
    def final_unit_price(self):
        return self.snapshot[5]

    def __str__(self):
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


# =============================================================================
# SECTION 5 — INVENTORY CLASS  (OOP: Inheritance)
# =============================================================================


class Inventory(Catalog):
    """
    Inherits from abstract Catalog.
    Implements display_all() and search() as required.
    Products stored in a DICT: { product_id -> Product object }
    """

    def __init__(self):
        # DATA STRUCTURE: dict — O(1) lookup by product_id
        self.__products = {}

    def add_product(self, product: Product):
        if product.product_id in self.__products:
            print(f"  [!] Product ID '{product.product_id}' already exists.")
        else:
            self.__products[product.product_id] = product
            print(f"  [+] '{product.name}' added to inventory.")

    def get_product(self, product_id):
        return self.__products.get(product_id, None)

    def all_products(self):
        # Returns list of all Product objects
        return list(self.__products.values())

    # OOP: implementing abstract method
    def display_all(self):
        if not self.__products:
            print("  No products in inventory.")
            return
        print(f"\n  {'─'*75}")
        print(f"  {'ID':<8} {'Name':<20} {'Price':>10} {'Category':<14} {'Stock':>6}")
        print(f"  {'─'*75}")
        for p in self.__products.values():
            print(f"  {p}")
        print(f"  {'─'*75}\n")

    # OOP: implementing abstract method
    def search(self, keyword):
        keyword = keyword.lower()
        # list comprehension + lambda-style inline filter
        results = [
            p
            for p in self.__products.values()
            if keyword in p.name.lower() or keyword in p.category.lower()
        ]
        return results

    def low_stock_alert(self, threshold=5):
        # LIST COMPREHENSION: filter products below threshold
        return [p for p in self.__products.values() if p.stock < threshold]

    def get_all_categories(self):
        # DATA STRUCTURE: set — unique categories only
        return set(p.category for p in self.__products.values())


# =============================================================================
# SECTION 6 — SALES MANAGER CLASS  (OOP: Composition / Controller)
# =============================================================================


class SalesManager:
    """
    Central controller.
    - Uses Inventory to manage products
    - Maintains customer registry (dict)
    - Maintains sales history (list)
    - Uses lambda, map, filter, reduce for analytics
    """

    # Predefined discount strategies as lambdas
    DISCOUNTS = {
        "none": lambda p: p,
        "10%": lambda p: round(p * 0.90, 2),
        "20%": lambda p: round(p * 0.80, 2),
        "festival": lambda p: round(p * 0.85, 2),  # 15% Dashain/Tihar discount
    }

    def __init__(self):
        self.inventory = Inventory()
        # DATA STRUCTURE: dict — { customer_id -> Customer }
        self.__customers = {}
        # DATA STRUCTURE: list — ordered sales history
        self.__sales = []

    # ------------------------------------------------------------------ #
    #  CUSTOMER METHODS
    # ------------------------------------------------------------------ #

    def register_customer(self, customer_id, name, phone):
        if customer_id in self.__customers:
            print(f"  [!] Customer ID '{customer_id}' already registered.")
        else:
            self.__customers[customer_id] = Customer(customer_id, name, phone)
            print(f"  [+] Customer '{name}' registered.")

    def get_customer(self, customer_id):
        return self.__customers.get(customer_id, None)

    def display_customers(self):
        if not self.__customers:
            print("  No customers registered yet.")
            return
        print(f"\n  {'─'*65}")
        for c in self.__customers.values():
            print(f"  {c}")
        print(f"  {'─'*65}\n")

    # ------------------------------------------------------------------ #
    #  SALES METHODS
    # ------------------------------------------------------------------ #

    def make_sale(self, customer_id, product_id, qty, discount_key="none"):
        customer = self.get_customer(customer_id)
        if not customer:
            print(f"  [!] Customer '{customer_id}' not found.")
            return

        product = self.inventory.get_product(product_id)
        if not product:
            print(f"  [!] Product '{product_id}' not found.")
            return

        if product.stock < qty:
            print(f"  [!] Not enough stock. Available: {product.stock}")
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

        # Deduct stock
        product.stock = product.stock - qty

        # Append to sales list
        self.__sales.append(sale)

        # Link sale to customer history
        customer.add_purchase(sale.sale_id)

        print(f"\n  ✅ Sale recorded!")
        print(f"  {sale}\n")

    # ------------------------------------------------------------------ #
    #  ANALYTICS METHODS  (map, filter, reduce, lambda, sorted)
    # ------------------------------------------------------------------ #

    def total_revenue(self):
        if not self.__sales:
            return 0.0
        # reduce() — accumulates total across all sales
        return reduce(lambda acc, sale: acc + sale.total, self.__sales, 0.0)

    def sales_report(self):
        if not self.__sales:
            print("  No sales recorded yet.")
            return

        print(f"\n  {'─'*85}")
        print("   SALES REPORT")
        print(f"  {'─'*85}")

        # map() — format each sale as a display string
        formatted = list(map(lambda s: f"  {s}", self.__sales))
        for line in formatted:
            print(line)

        print(f"  {'─'*85}")
        print(f"  TOTAL REVENUE : Rs.{self.total_revenue():,.2f}")
        print(f"  TOTAL SALES   : {len(self.__sales)}")
        print(f"  {'─'*85}\n")

    def revenue_by_category(self):
        """
        Groups revenue by product category.
        Uses dict comprehension + filter + reduce.
        """
        categories = self.inventory.get_all_categories()
        report = {}

        for cat in categories:
            # filter(): only sales for products in this category
            cat_sales = list(
                filter(
                    lambda s: self.inventory.get_product(s.product_id) is not None
                    and self.inventory.get_product(s.product_id).category == cat,
                    self.__sales,
                )
            )
            if cat_sales:
                # reduce(): sum revenue for this category
                cat_revenue = reduce(lambda acc, s: acc + s.total, cat_sales, 0.0)
                report[cat] = cat_revenue

        return report

    def top_products(self, n=3):
        """
        Returns top N products by revenue generated.
        Uses dict to accumulate, then sorted() + lambda.
        """
        revenue_map = {}  # DATA STRUCTURE: dict { product_id: total_revenue }

        for sale in self.__sales:
            if sale.product_id not in revenue_map:
                revenue_map[sale.product_id] = {
                    "name": sale.product_name,
                    "revenue": 0.0,
                    "qty": 0,
                }
            revenue_map[sale.product_id]["revenue"] += sale.total
            revenue_map[sale.product_id]["qty"] += sale.qty

        # sorted() + lambda — sort by revenue descending
        sorted_products = sorted(
            revenue_map.items(), key=lambda item: item[1]["revenue"], reverse=True
        )
        return sorted_products[:n]

    def unique_buyers_today(self):
        """
        Returns a SET of customer IDs who bought something today.
        SET: ensures each customer counted once.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # set comprehension
        return {s.customer_id for s in self.__sales if s.timestamp.startswith(today)}

    def customer_history(self, customer_id):
        customer = self.get_customer(customer_id)
        if not customer:
            print(f"  [!] Customer not found.")
            return

        print(f"\n  Purchase history for {customer.name}:")
        print(f"  {'─'*85}")

        # filter() — only this customer's sales
        cust_sales = list(filter(lambda s: s.customer_id == customer_id, self.__sales))

        if not cust_sales:
            print("  No purchases yet.")
        else:
            for s in cust_sales:
                print(f"  {s}")
            cust_total = reduce(lambda acc, s: acc + s.total, cust_sales, 0.0)
            print(f"  {'─'*85}")
            print(f"  Total Spent: Rs.{cust_total:,.2f}\n")

    def low_stock_report(self, threshold=5):
        alerts = self.inventory.low_stock_alert(threshold)
        if not alerts:
            print(f"  All products have stock above {threshold}.")
        else:
            print(f"\n  ⚠️  LOW STOCK ALERT (threshold: {threshold})")
            print(f"  {'─'*50}")
            for p in alerts:
                print(f"  {p}")
            print(f"  {'─'*50}\n")


# =============================================================================
# SECTION 7 — HELPER FUNCTIONS  (standalone functions)
# =============================================================================


def print_header(title):
    """Utility function for clean section headers."""
    print(f"\n  {'═'*60}")
    print(f"   {title}")
    print(f"  {'═'*60}")


def get_int_input(prompt, min_val=1):
    """Safe integer input with validation."""
    while True:
        try:
            val = int(input(prompt))
            if val < min_val:
                print(f"  [!] Must be at least {min_val}.")
            else:
                return val
        except ValueError:
            print("  [!] Enter a valid number.")


def seed_demo_data(manager: SalesManager):
    """
    Pre-loads demo data so you can test immediately.
    Uses a list of tuples to define products compactly.
    """

    # DATA STRUCTURE: list of tuples — compact product definitions
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

    # map() to create Product objects from tuple data
    product_objects = list(
        map(lambda t: Product(t[0], t[1], t[2], t[3], t[4]), products)
    )

    for p in product_objects:
        manager.inventory.add_product(p)

    # Customers
    customers = [
        ("C001", "Aarav Sharma", "9841000001"),
        ("C002", "Sita Thapa", "9852000002"),
        ("C003", "Bikash Karki", "9863000003"),
    ]
    for cid, name, phone in customers:
        manager.register_customer(cid, name, phone)

    # Some initial sales
    manager.make_sale("C001", "P001", 1, "10%")
    manager.make_sale("C001", "P002", 2, "none")
    manager.make_sale("C002", "P003", 3, "festival")
    manager.make_sale("C003", "P007", 1, "20%")
    manager.make_sale("C002", "P004", 1, "none")

    print("\n  ✅ Demo data loaded successfully!\n")


# =============================================================================
# SECTION 8 — MAIN MENU  (CLI Loop)
# =============================================================================


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

        # ── 1. View All Products ──────────────────────────────────────
        if choice == "1":
            print_header("ALL PRODUCTS")
            manager.inventory.display_all()

        # ── 2. Add New Product ────────────────────────────────────────
        elif choice == "2":
            print_header("ADD NEW PRODUCT")
            pid = input("  Product ID   : ").strip()
            name = input("  Name         : ").strip()
            price = float(input("  Price (Rs.)  : "))
            category = input("  Category     : ").strip()
            stock = get_int_input("  Stock qty    : ", min_val=0)
            manager.inventory.add_product(Product(pid, name, price, category, stock))

        # ── 3. Search Products ────────────────────────────────────────
        elif choice == "3":
            print_header("SEARCH PRODUCTS")
            kw = input("  Enter keyword (name or category): ").strip()
            results = manager.inventory.search(kw)
            if not results:
                print("  No products matched.")
            else:
                for p in results:
                    print(f"  {p}")

        # ── 4. Make a Sale ────────────────────────────────────────────
        elif choice == "4":
            print_header("MAKE A SALE")
            cid = input("  Customer ID : ").strip()
            pid = input("  Product ID  : ").strip()
            qty = get_int_input("  Quantity    : ")
            print("  Discount options: none | 10% | 20% | festival")
            disc = input("  Discount key: ").strip().lower()
            if disc not in SalesManager.DISCOUNTS:
                print("  [!] Unknown discount key — applying 'none'.")
                disc = "none"
            manager.make_sale(cid, pid, qty, disc)

        # ── 5. Sales Report ───────────────────────────────────────────
        elif choice == "5":
            print_header("SALES REPORT")
            manager.sales_report()

        # ── 6. Revenue by Category ────────────────────────────────────
        elif choice == "6":
            print_header("REVENUE BY CATEGORY")
            report = manager.revenue_by_category()
            if not report:
                print("  No sales data yet.")
            else:
                print(f"  {'─'*40}")
                # sorted by revenue desc using lambda
                for cat, rev in sorted(
                    report.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"  {cat:<15} : Rs.{rev:>12,.2f}")
                print(f"  {'─'*40}")

        # ── 7. Top Products ───────────────────────────────────────────
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

        # ── 8. View All Customers ─────────────────────────────────────
        elif choice == "8":
            print_header("ALL CUSTOMERS")
            manager.display_customers()

        # ── 9. Customer Purchase History ──────────────────────────────
        elif choice == "9":
            print_header("CUSTOMER HISTORY")
            cid = input("  Enter Customer ID: ").strip()
            manager.customer_history(cid)

        # ── 10. Low Stock Alert ───────────────────────────────────────
        elif choice == "10":
            print_header("LOW STOCK ALERT")
            manager.low_stock_report(threshold=5)

        # ── 11. Unique Buyers Today ───────────────────────────────────
        elif choice == "11":
            print_header("UNIQUE BUYERS TODAY")
            buyers = manager.unique_buyers_today()
            if not buyers:
                print("  No sales recorded today.")
            else:
                print(f"  {len(buyers)} unique buyer(s) today: {', '.join(buyers)}\n")

        # ── 12. Update Product Price ──────────────────────────────────
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

        # ── 0. Exit ───────────────────────────────────────────────────
        elif choice == "0":
            print("\n  Goodbye! 👋\n")
            break

        else:
            print("  [!] Invalid choice. Try again.")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
