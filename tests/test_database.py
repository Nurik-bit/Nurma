import sys
import os
import unittest
from datetime import datetime

# Добавляем папку app в путь поиска
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

# Импортируем функции из database.py
import database


class TestDatabase(unittest.TestCase):
    def test_connection(self):
        conn = database.create_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_save_and_fetch_translation(self):
        source_text = "Привет"
        translated_text = "Hello"
        source_language = "ru"
        target_language = "en"
        translation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        database.init_db()  # Обязательно инициализируем БД
        database.save_translation(
            source_text,
            translated_text,
            source_language,
            target_language,
            translation_date,
        )

        history = database.get_translation_history()
        self.assertTrue(
            any(row[1] == source_text and row[2] == translated_text for row in history)
        )

    def test_delete_translation(self):
        # Добавляем перевод
        source_text = "Удалить это"
        translated_text = "Delete this"
        source_language = "ru"
        target_language = "en"
        translation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        database.save_translation(
            source_text,
            translated_text,
            source_language,
            target_language,
            translation_date,
        )

        # Получаем последний translation_id
        history = database.get_translation_history()
        last_id = history[-1][0]  # Первый столбец — это id

        database.delete_translation(last_id)

        # Проверяем, что его больше нет в истории
        updated_history = database.get_translation_history()
        self.assertFalse(any(row[0] == last_id for row in updated_history))


if __name__ == "__main__":
    unittest.main()
