import sys
import os
import sqlite3
import unittest

# Добавляем корневую папку проекта в sys.path для использования абсолютных импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import app
from app.database import init_db, save_translation, get_translation_history

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "translations.db")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Удалим старую базу, чтобы начать заново
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def tearDown(self):
        # Удаление базы после каждого теста
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def test_database_connection(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        self.assertIn(("translations",), tables)
        self.assertIn(("translation_history",), tables)

    def test_save_and_retrieve_translation(self):
        save_translation("Hello", "Привет", "en", "ru", "2025-04-21")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT source_text, translated_text FROM translations WHERE source_text = 'Hello';"
        )
        result = cursor.fetchone()
        conn.close()
        self.assertEqual(result, ("Hello", "Привет"))

    def test_get_translation_history(self):
        save_translation("Test", "Тест", "en", "ru", "2025-04-21")
        history = get_translation_history()
        self.assertTrue(any("Test" in row for row in [str(r) for r in history]))


def test_flask_app(self):
    with app.test_client() as client:
        response = client.post(
            "/",
            data={"text": "Hello", "source_language": "en", "target_language": "ru"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Привет", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
