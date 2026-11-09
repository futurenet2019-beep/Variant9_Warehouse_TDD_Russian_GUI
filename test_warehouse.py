import unittest
import tempfile
import os

from warehouse import Warehouse


class TestWarehouseTDD(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_warehouse.db")
        self.warehouse = Warehouse(self.db_path)

    def tearDown(self):
        self.warehouse.close()
        self.temp_dir.cleanup()

    def test_add_new_product(self):
        product_id = self.warehouse.add_product("Ноутбук", 10)
        self.assertEqual(self.warehouse.get_quantity(product_id), 10)
    def test_search_products_by_name(self):
        self.warehouse.add_product("Ноутбук Lenovo", 5)
        self.warehouse.add_product("Ноутбук HP", 3)
        self.warehouse.add_product("Монитор Samsung", 8)

        results = self.warehouse.search_products("Ноутбук")

        self.assertEqual(len(results), 2)
        self.assertTrue(
            all("Ноутбук" in product["name"] for product in results)
        )
    def test_duplicate_product_is_rejected(self):
        self.warehouse.add_product("Ноутбук", 2)
        with self.assertRaises(ValueError):
            self.warehouse.add_product("Ноутбук", 3)

    def test_receive_goods_increases_stock(self):
        product_id = self.warehouse.add_product("Монитор", 10)
        result = self.warehouse.receive_goods(product_id, 5)
        self.assertEqual(result, 15)

    def test_ship_goods_decreases_stock(self):
        product_id = self.warehouse.add_product("Мышь", 10)
        result = self.warehouse.ship_goods(product_id, 4)
        self.assertEqual(result, 6)

    def test_ship_more_than_stock_is_rejected(self):
        product_id = self.warehouse.add_product("Клавиатура", 3)
        with self.assertRaises(ValueError):
            self.warehouse.ship_goods(product_id, 5)
        self.assertEqual(self.warehouse.get_quantity(product_id), 3)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.warehouse.add_product("Принтер", -1)

    def test_update_quantity(self):
        product_id = self.warehouse.add_product("Кабель", 10)
        self.warehouse.update_quantity(product_id, 7)
        self.assertEqual(self.warehouse.get_quantity(product_id), 7)

    def test_movement_history_is_recorded(self):
        product_id = self.warehouse.add_product("Флешка", 2)
        self.warehouse.receive_goods(product_id, 5)
        history = self.warehouse.get_movements(product_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["movement_type"], "Поступление")

    def test_zero_or_negative_movement_is_rejected(self):
        product_id = self.warehouse.add_product("SSD", 5)
        with self.assertRaises(ValueError):
            self.warehouse.receive_goods(product_id, 0)
        with self.assertRaises(ValueError):
            self.warehouse.ship_goods(product_id, -2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
