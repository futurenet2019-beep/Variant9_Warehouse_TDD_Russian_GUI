import sqlite3
from datetime import datetime


class Warehouse:
    """Бизнес-логика системы управления складом."""

    def __init__(self, db_path="warehouse.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    quantity REAL NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                    unit TEXT NOT NULL DEFAULT 'шт.'
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL,
                    quantity REAL NOT NULL CHECK(quantity > 0),
                    date TEXT NOT NULL,
                    note TEXT,
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )
            """)

    def add_product(self, name, quantity=0, unit="шт."):
        name = name.strip()
        unit = unit.strip() or "шт."
        quantity = float(quantity)
        if not name:
            raise ValueError("Название товара не может быть пустым.")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным.")
        try:
            with self.conn:
                cur = self.conn.execute(
                    "INSERT INTO products(name, quantity, unit) VALUES (?, ?, ?)",
                    (name, quantity, unit)
                )
                product_id = cur.lastrowid
                if quantity > 0:
                    self._add_movement(product_id, "Поступление", quantity, "Начальный остаток")
                return product_id
        except sqlite3.IntegrityError as exc:
            raise ValueError("Товар с таким названием уже существует.") from exc

    def update_quantity(self, product_id, new_quantity, note="Корректировка остатка"):
        new_quantity = float(new_quantity)
        if new_quantity < 0:
            raise ValueError("Количество не может быть отрицательным.")
        with self.conn:
            row = self._get_product_row(product_id)
            if row is None:
                raise ValueError("Товар не найден.")
            difference = new_quantity - row["quantity"]
            self.conn.execute(
                "UPDATE products SET quantity=? WHERE id=?",
                (new_quantity, product_id)
            )
            if difference > 0:
                self._add_movement(product_id, "Поступление", difference, note)
            elif difference < 0:
                self._add_movement(product_id, "Отгрузка", abs(difference), note)
        return new_quantity

    def receive_goods(self, product_id, quantity, note="Поступление товара"):
        quantity = self._validate_positive(quantity)
        with self.conn:
            row = self._get_product_row(product_id)
            if row is None:
                raise ValueError("Товар не найден.")
            self.conn.execute(
                "UPDATE products SET quantity=quantity+? WHERE id=?",
                (quantity, product_id)
            )
            self._add_movement(product_id, "Поступление", quantity, note)
        return self.get_quantity(product_id)

    def ship_goods(self, product_id, quantity, note="Отгрузка товара"):
        quantity = self._validate_positive(quantity)
        with self.conn:
            row = self._get_product_row(product_id)
            if row is None:
                raise ValueError("Товар не найден.")
            if row["quantity"] < quantity:
                raise ValueError(
                    f"Недостаточно товара на складе. Остаток: {row['quantity']:g}, "
                    f"требуется: {quantity:g}."
                )
            self.conn.execute(
                "UPDATE products SET quantity=quantity-? WHERE id=?",
                (quantity, product_id)
            )
            self._add_movement(product_id, "Отгрузка", quantity, note)
        return self.get_quantity(product_id)

    def get_quantity(self, product_id):
        row = self._get_product_row(product_id)
        return float(row["quantity"]) if row else 0.0

    def get_product(self, product_id):
        row = self._get_product_row(product_id)
        return dict(row) if row else None

    def get_products(self):
        rows = self.conn.execute(
            "SELECT id, name, quantity, unit FROM products ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_movements(self, product_id=None):
        query = """
            SELECT m.id, p.name AS product_name, m.movement_type,
                   m.quantity, m.date, m.note
            FROM movements m
            JOIN products p ON p.id=m.product_id
        """
        params = ()
        if product_id is not None:
            query += " WHERE m.product_id=?"
            params = (product_id,)
        query += " ORDER BY m.id DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def _get_product_row(self, product_id):
        return self.conn.execute(
            "SELECT id, name, quantity, unit FROM products WHERE id=?",
            (product_id,)
        ).fetchone()

    def _add_movement(self, product_id, movement_type, quantity, note):
        self.conn.execute(
            """INSERT INTO movements(product_id, movement_type, quantity, date, note)
               VALUES (?, ?, ?, ?, ?)""",
            (product_id, movement_type, quantity,
             datetime.now().strftime("%d.%m.%Y %H:%M:%S"), note)
        )

    @staticmethod
    def _validate_positive(quantity):
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля.")
        return quantity

    def close(self):
        self.conn.close()
