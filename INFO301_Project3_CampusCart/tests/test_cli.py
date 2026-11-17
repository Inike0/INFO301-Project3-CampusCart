"""Live console process checks (including restart) using a temporary CSV folder."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import ShopStore

APP = Path(__file__).resolve().parents[1] / "app.py"


class CommandLineTests(unittest.TestCase):
    def test_confirmed_order_and_persistence_across_processes(self):
        with tempfile.TemporaryDirectory() as folder:
            shop = ShopStore(folder)
            customer = shop.register_customer("Test Customer")
            product = shop.add_product("USB Drive", "12.00", 4)
            command = [sys.executable, str(APP), "--data-dir", folder]
            scripted = f"4\n{customer}\n1\n{product}\n2\n2\n5\ny\n7\n"
            first = subprocess.run(command, input=scripted, capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("$24.00", first.stdout)
            self.assertIn("ORDER CONFIRMED: O001", first.stdout)
            self.assertEqual(ShopStore(folder).find_product(product)["stock"], "2")
            second = subprocess.run(command, input="5\n2\nO001\n7\n", capture_output=True, text=True, timeout=10)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("USB Drive", second.stdout)
            self.assertIn("O001", second.stdout)

    def test_invalid_menu_option_is_handled_without_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run([sys.executable, str(APP), "--data-dir", folder],
                                 input="wrong\n99\n7\n", capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertGreaterEqual(run.stdout.count("Invalid menu option"), 2)


if __name__ == "__main__":
    unittest.main()
