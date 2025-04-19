import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os

# Добавляем путь к родительской директории, чтобы импортировать приложение
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database  # Импортируем файл с функциями для работы с базой данных

class TestDatabaseFunctions(unittest.TestCase):
    
    @patch('database.sqlite3.connect')
    def test_create_connection(self, mock_connect):
        """Тестируем создание соединения с базой данных"""
        # Мокаем соединение, чтобы не подключаться к реальной базе данных
        mock_connect.return_value = MagicMock(spec=sqlite3.Connection)
        
        conn = database.create_connection()
        
        self.assertIsInstance(conn, sqlite3.Connection)
        mock_connect.assert_called_once_with(database.DATABASE_PATH)

    @patch('database.sqlite3.connect')
    def test_init_db(self, mock_connect):
        """Тестируем инициализацию базы данных (создание таблиц)"""
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Вызываем функцию инициализации базы данных
        database.init_db()
        
        # Проверяем, что были выполнены команды для создания таблиц
        mock_cursor.execute.assert_any_call('''CREATE TABLE IF NOT EXISTS translations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_text TEXT NOT NULL,
                        translated_text TEXT NOT NULL
                    )''')
        mock_cursor.execute.assert_any_call('''CREATE TABLE IF NOT EXISTS translation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        translation_id INTEGER NOT NULL,
                        source_language TEXT NOT NULL,
                        target_language TEXT NOT NULL,
                        translation_date TEXT NOT NULL,
                        FOREIGN KEY (translation_id) REFERENCES translations(id)
                    )''')
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('database.create_connection')
    @patch('database.sqlite3.Connection.cursor')
    def test_save_translation(self, mock_cursor, mock_create_connection):
        """Тестируем сохранение перевода в базу данных"""
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_cursor.return_value = mock_cursor
        mock_create_connection.return_value = mock_conn
        
        # Мокаем вставку данных в таблицы
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        source_text = "Hello"
        translated_text = "Привет"
        source_language = "en"
        target_language = "ru"
        translation_date = "2025-04-19"
        
        # Вызываем функцию сохранения
        database.save_translation(source_text, translated_text, source_language, target_language, translation_date)
        
        # Проверяем, что была выполнена вставка данных в таблицы
        mock_cursor.execute.assert_any_call("INSERT INTO translations (source_text, translated_text) VALUES (?, ?)", 
                                            (source_text, translated_text))
        mock_cursor.execute.assert_any_call("INSERT INTO translation_history (translation_id, source_language, target_language, translation_date) VALUES (?, ?, ?, ?)", 
                                            (1, source_language, target_language, translation_date))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('database.create_connection')
    def test_get_translation_history(self, mock_create_connection):
        """Тестируем получение истории переводов"""
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Мокаем возвращаемое значение для истории переводов
        mock_cursor.fetchall.return_value = [
            (1, 'Hello', 'Привет', 'en', 'ru', '2025-04-19')
        ]
        
        history = database.get_translation_history()
        
        # Проверяем, что история переводов была получена
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][1], 'Hello')  # Ожидаем, что source_text = 'Hello'
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.database.sqlite3.connect')
    def test_delete_translation(self, mock_connect):
        """Тестируем удаление записи о переводе"""
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_cursor = MagicMock(spec=sqlite3.Cursor)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Мокаем выполнение запроса на удаление
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        translation_id = 1
        
        # Вызываем функцию удаления
        database.delete_translation(translation_id)
        
        # Проверяем, что запрос на удаление был вызван
        mock_cursor.execute.assert_any_call('DELETE FROM translation_history WHERE translation_id = ?', (translation_id,))
        mock_cursor.execute.assert_any_call('DELETE FROM translations WHERE id = ?', (translation_id,))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
