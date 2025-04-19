import unittest
from unittest.mock import patch, MagicMock
from app import app  # Импортируем Flask-приложение из app.py
import sqlite3
import os


class TestAppDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        """Устанавливаем приложение Flask для тестирования."""
        self.app = app.test_client()
        self.app.testing = True

        # Убедимся, что база данных чистая перед каждым тестом
        self.db_path = os.path.join(
            os.path.dirname(__file__), "database", "translations.db"
        )
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self._create_test_db()

    def _create_test_db(self):
        """Создаем тестовую базу данных для интеграционных тестов."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем таблицы, если их нет
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS translations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            source_text TEXT NOT NULL,
                            translated_text TEXT NOT NULL
                        )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS translation_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            translation_id INTEGER NOT NULL,
                            source_language TEXT NOT NULL,
                            target_language TEXT NOT NULL,
                            translation_date TEXT NOT NULL,
                            FOREIGN KEY (translation_id) REFERENCES translations(id)
                        )"""
        )
        conn.commit()
        conn.close()

    def test_post_translation_and_save_to_db(self):
        """Тестируем POST-запрос на добавление перевода и его сохранение в базу данных."""
        response = self.app.post(
            "/",
            data={"text": "Hello", "source_language": "en", "target_language": "ru"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Привет", response.data.decode("utf-8"))

        # Проверим, что перевод сохранен в базе данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM translations WHERE source_text = 'Hello' AND translated_text = 'Привет'"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()

    def test_get_translation_history(self):
        """Тестируем получение истории переводов через Flask."""
        # Добавим тестовый перевод напрямую в базу
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO translations (source_text, translated_text) VALUES (?, ?)",
            ("Hello", "Привет"),
        )
        translation_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO translation_history (translation_id, source_language, target_language, translation_date) VALUES (?, ?, ?, ?)",
            (translation_id, "en", "ru", "2025-04-19"),
        )
        conn.commit()
        conn.close()

        # Запросим историю переводов
        response = self.app.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Привет", response.data.decode("utf-8"))

    def test_delete_translation(self):
        """Тестируем удаление перевода из базы данных через Flask."""
        # Добавим тестовый перевод в базу
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO translations (source_text, translated_text) VALUES (?, ?)",
            ("Hello", "Привет"),
        )
        translation_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO translation_history (translation_id, source_language, target_language, translation_date) VALUES (?, ?, ?, ?)",
            (translation_id, "en", "ru", "2025-04-19"),
        )
        conn.commit()
        conn.close()

        # Убедимся, что перевод был добавлен
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM translations WHERE id = ?", (translation_id,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()

        # Сделаем запрос на удаление перевода
        response = self.app.get(
            f"/delete_history/{translation_id}", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        # Проверим, что перевод был удален из базы данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM translations WHERE id = ?", (translation_id,))
        result = cursor.fetchone()
        self.assertIsNone(result)
        conn.close()

    def tearDown(self):
        """Очистка после каждого теста (удаляем базу данных)."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)


if __name__ == "__main__":
    unittest.main()
