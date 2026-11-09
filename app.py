import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from warehouse import Warehouse


class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления складом — Вариант 9 (TDD)")
        self.root.geometry("980x620")
        self.root.minsize(850, 520)

        self.warehouse = Warehouse("warehouse.db")
        self._build_ui()
        self.refresh_products()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        header = ttk.Label(
            self.root,
            text="СИСТЕМА УПРАВЛЕНИЯ СКЛАДОМ",
            font=("Arial", 18, "bold")
        )
        header.pack(pady=(12, 4))

        subtitle = ttk.Label(
            self.root,
            text="Вариант 9 • Разработка с использованием TDD",
            font=("Arial", 10)
        )
        subtitle.pack(pady=(0, 10))

        form = ttk.LabelFrame(self.root, text="Добавление нового товара")
        form.pack(fill="x", padx=14, pady=6)

        ttk.Label(form, text="Название товара:").grid(row=0, column=0, padx=8, pady=8)
        self.name_entry = ttk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form, text="Начальное количество:").grid(row=0, column=2, padx=8, pady=8)
        self.quantity_entry = ttk.Entry(form, width=14)
        self.quantity_entry.insert(0, "0")
        self.quantity_entry.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form, text="Единица:").grid(row=0, column=4, padx=8, pady=8)
        self.unit_entry = ttk.Entry(form, width=9)
        self.unit_entry.insert(0, "шт.")
        self.unit_entry.grid(row=0, column=5, padx=8, pady=8)

        ttk.Button(form, text="Добавить товар", command=self.add_product).grid(
            row=0, column=6, padx=8, pady=8
        )

        table_frame = ttk.LabelFrame(self.root, text="Товары и остатки на складе")
        table_frame.pack(fill="both", expand=True, padx=14, pady=6)

        columns = ("id", "name", "quantity", "unit")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название товара")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("unit", text="Единица измерения")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=430)
        self.tree.column("quantity", width=180, anchor="center")
        self.tree.column("unit", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        actions = ttk.Frame(self.root)
        actions.pack(fill="x", padx=14, pady=10)

        ttk.Button(actions, text="Поступление товара", command=self.receive_goods).pack(
            side="left", padx=5
        )
        ttk.Button(actions, text="Отгрузка товара", command=self.ship_goods).pack(
            side="left", padx=5
        )
        ttk.Button(actions, text="Изменить остаток", command=self.update_quantity).pack(
            side="left", padx=5
        )
        ttk.Button(actions, text="История операций", command=self.show_history).pack(
            side="left", padx=5
        )
        ttk.Button(actions, text="Обновить", command=self.refresh_products).pack(
            side="right", padx=5
        )

        self.status_label = ttk.Label(self.root, text="Статус: система готова")
        self.status_label.pack(pady=(0, 8))

    def selected_product(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите товар в таблице.")
            return None
        values = self.tree.item(selection[0], "values")
        return int(values[0]), values[1]

    @staticmethod
    def parse_quantity(value):
        try:
            quantity = float(value.strip().replace(",", "."))
        except (ValueError, AttributeError):
            raise ValueError("Введите корректное число.")
        return quantity

    def add_product(self):
        name = self.name_entry.get().strip()
        try:
            quantity = self.parse_quantity(self.quantity_entry.get())
            unit = self.unit_entry.get().strip() or "шт."
            self.warehouse.add_product(name, quantity, unit)
            self.refresh_products()
            self.name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, "0")
            self.status_label.config(text="Статус: товар добавлен")
            messagebox.showinfo("Успешно", "Товар успешно добавлен.")
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))

    def receive_goods(self):
        selected = self.selected_product()
        if not selected:
            return
        product_id, product_name = selected
        value = simpledialog.askstring(
            "Поступление товара",
            f"Введите количество поступившего товара «{product_name}»:",
            parent=self.root
        )
        if value is None:
            return
        try:
            quantity = self.parse_quantity(value)
            balance = self.warehouse.receive_goods(product_id, quantity)
            self.refresh_products()
            self.status_label.config(text=f"Статус: поступление выполнено; остаток {balance:g}")
            messagebox.showinfo("Успешно", f"Товар поступил.\nТекущий остаток: {balance:g}")
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))

    def ship_goods(self):
        selected = self.selected_product()
        if not selected:
            return
        product_id, product_name = selected
        value = simpledialog.askstring(
            "Отгрузка товара",
            f"Введите количество отгружаемого товара «{product_name}»:",
            parent=self.root
        )
        if value is None:
            return
        try:
            quantity = self.parse_quantity(value)
            balance = self.warehouse.ship_goods(product_id, quantity)
            self.refresh_products()
            self.status_label.config(text=f"Статус: отгрузка выполнена; остаток {balance:g}")
            messagebox.showinfo("Успешно", f"Товар отгружен.\nТекущий остаток: {balance:g}")
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))

    def update_quantity(self):
        selected = self.selected_product()
        if not selected:
            return
        product_id, product_name = selected
        current = self.warehouse.get_quantity(product_id)
        value = simpledialog.askstring(
            "Изменение остатка",
            f"Текущий остаток товара «{product_name}»: {current:g}\n"
            "Введите новое количество:",
            parent=self.root
        )
        if value is None:
            return
        try:
            quantity = self.parse_quantity(value)
            balance = self.warehouse.update_quantity(product_id, quantity)
            self.refresh_products()
            self.status_label.config(text=f"Статус: остаток изменен на {balance:g}")
            messagebox.showinfo("Успешно", f"Остаток обновлен: {balance:g}")
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))

    def show_history(self):
        window = tk.Toplevel(self.root)
        window.title("История поступления и отгрузки")
        window.geometry("850x420")

        columns = ("id", "product", "type", "quantity", "date", "note")
        tree = ttk.Treeview(window, columns=columns, show="headings")
        labels = {
            "id": "№",
            "product": "Товар",
            "type": "Тип операции",
            "quantity": "Количество",
            "date": "Дата и время",
            "note": "Комментарий"
        }
        widths = {"id": 50, "product": 180, "type": 140, "quantity": 100, "date": 160, "note": 200}
        for col in columns:
            tree.heading(col, text=labels[col])
            tree.column(col, width=widths[col], anchor="center" if col in ("id", "quantity") else "w")

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        for movement in self.warehouse.get_movements():
            tree.insert("", "end", values=(
                movement["id"], movement["product_name"],
                movement["movement_type"], movement["quantity"],
                movement["date"], movement["note"] or ""
            ))

    def refresh_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in self.warehouse.get_products():
            self.tree.insert("", "end", values=(
                product["id"], product["name"], product["quantity"], product["unit"]
            ))

    def on_close(self):
        self.warehouse.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()
