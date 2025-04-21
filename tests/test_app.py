import sys
import os
import unittest

# Устанавливаем корень проекта в путь поиска
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Абсолютный импорт приложения
from app.app import app  # Импортируем приложение Flask из папки app


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Этот метод выполняется один раз перед всеми тестами"""
        cls.client = app.test_client()  # Получаем клиент для тестирования

    def test_example(self):
        """Пример простого теста, который проверяет статус код"""
        response = self.client.get("/")  # Отправляем GET-запрос на главную страницу
        self.assertEqual(
            response.status_code, 200
        )  # Проверяем, что ответ имеет код 200

    def test_another_example(self):
        """Пример другого теста"""
        response = self.client.get("/nonexistent")  # Страница не существует
        self.assertEqual(
            response.status_code, 404
        )  # Проверяем, что ответ имеет код 404


if __name__ == "__main__":
    unittest.main()
