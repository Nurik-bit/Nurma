import unittest
from unittest.mock import patch, MagicMock
from app.app import app  # Исправленный импорт приложения
from app.database import (
    init_db,
    save_translation,
    get_translation_history,
    delete_translation
)

class TestTranslatorApp(unittest.TestCase):
    def setUp(self):
        # Создание тестового клиента для Flask
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.app.translator.translate')
    @patch('app.app.save_translation')
    @patch('app.app.log_and_report_translation')
    def test_index_post_translation(self, mock_log, mock_save, mock_translate):
        # Мокаем вызов translate, чтобы вернуть поддельный перевод
        mock_translate.return_value = MagicMock(text='Привет')

        # Отправляем POST-запрос с данными формы
        response = self.app.post('/', data={
            'text': 'Hello',
            'source_language': 'en',
            'target_language': 'ru'
        })

        # Проверяем, что статус ответа 200 (успех)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что текст на странице содержит переведенный текст
        self.assertIn('Привет', response.data.decode('utf-8'))

        # Проверяем, что функции мока были вызваны
        mock_translate.assert_called_once()
        mock_save.assert_called_once()
        mock_log.assert_called_once()

    @patch('app.app.get_translation_history')
    def test_history_page(self, mock_history):
        # Мокаем функцию get_translation_history, чтобы вернуть поддельные данные
        mock_history.return_value = [
            {'original': 'Hello', 'translated': 'Привет', 'src_lang': 'en', 'tgt_lang': 'ru', 'date': '2025-04-19'}
        ]
        
        # Отправляем GET-запрос на страницу истории переводов
        response = self.app.get('/history')

        # Проверяем, что статус ответа 200 (успех)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что переведенный текст находится в ответе
        self.assertIn('Привет', response.data.decode('utf-8'))

    @patch('app.app.delete_translation')
    def test_delete_history(self, mock_delete):
        # Мокаем функцию delete_translation, чтобы она не взаимодействовала с реальной базой данных
        mock_delete.return_value = None

        # Отправляем GET-запрос для удаления перевода
        response = self.app.get('/delete_history/1', follow_redirects=True)

        # Проверяем, что после удаления мы перенаправлены обратно на страницу истории
        self.assertEqual(response.status_code, 200)

        # Проверяем, что delete_translation был вызван
        mock_delete.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
