import sys
import os

# Добавляем папку app в путь поиска
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

# Теперь импортируем приложение
from app import app  # Импортируем app из папки app

# Ваши тесты здесь, например:
import unittest


class TestApp(unittest.TestCase):

    def test_example(self):
        self.assertTrue(True)  # Пример простого теста


if __name__ == "__main__":
    unittest.main()
