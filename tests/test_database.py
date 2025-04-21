import sys
import os

# Добавляем папку app в путь поиска
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

# Импортируем необходимые модули из app
from database import Database  # Убедитесь, что класс Database есть в database.py

import unittest


class TestDatabase(unittest.TestCase):

    def test_database_connection(self):
        db = Database()
        result = db.connect()  # Пример вызова метода подключения
        self.assertTrue(
            result
        )  # Проверяем, что соединение прошло успешно (или возвращает True)

    def test_insert_data(self):
        db = Database()
        result = db.insert_data("example data")  # Пример вставки данных
        self.assertTrue(result)  # Проверка, что данные успешно вставлены


if __name__ == "__main__":
    unittest.main()
