import sqlite3
import os
from datetime import datetime

# Путь к базе данных
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "database", "translations.db"
)

# Путь к логам и отчетам
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "log.log")
REPORT_FILE_PATH = os.path.join(REPORTS_DIR, "report.html")


def create_connection():
    """Создаём соединение с базой данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def init_db():
    """Инициализация базы данных, создание таблиц."""
    conn = create_connection()
    cursor = conn.cursor()

    # Создание таблицы для переводов
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS translations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_text TEXT NOT NULL,
                        translated_text TEXT NOT NULL
                    )"""
    )

    # Создание таблицы для истории переводов с внешним ключом
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


def log_and_report_translation(
    source_text, translated_text, source_language, target_language, translation_date
):
    """Сохраняет лог и добавляет запись в HTML-отчет."""
    log_entry = (
        f"[{translation_date}] Перевод: '{source_text}' ({source_language}) → "
        f"'{translated_text}' ({target_language})\n"
    )

    # Лог
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    # HTML отчет
    html_entry = (
        f"<tr>"
        f"<td>{translation_date}</td>"
        f"<td>{source_language}</td>"
        f"<td>{target_language}</td>"
        f"<td>{source_text}</td>"
        f"<td>{translated_text}</td>"
        f"</tr>\n"
    )

    if not os.path.exists(REPORT_FILE_PATH):
        with open(REPORT_FILE_PATH, "w", encoding="utf-8") as report_file:
            report_file.write(
                """
                <html>
                <head>
                    <meta charset='utf-8'>
                    <title>Отчёт переводов</title>
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    <h2>История переводов</h2>
                    <table>
                        <tr>
                            <th>Дата</th>
                            <th>Язык источника</th>
                            <th>Язык перевода</th>
                            <th>Оригинал</th>
                            <th>Перевод</th>
                        </tr>
            """
            )

    with open(REPORT_FILE_PATH, "a", encoding="utf-8") as report_file:
        report_file.write(html_entry)


def save_translation(
    source_text, translated_text, source_language, target_language, translation_date
):
    """Сохраняем перевод в таблицы translations и translation_history."""
    conn = create_connection()
    cursor = conn.cursor()

    # Вставляем данные в таблицу translations
    cursor.execute(
        "INSERT INTO translations (source_text, translated_text) VALUES (?, ?)",
        (source_text, translated_text),
    )
    translation_id = cursor.lastrowid  # Получаем ID последней вставленной строки

    # Вставляем метаданные перевода в таблицу translation_history
    cursor.execute(
        "INSERT INTO translation_history (translation_id, source_language, target_language, translation_date) VALUES (?, ?, ?, ?)",
        (translation_id, source_language, target_language, translation_date),
    )

    conn.commit()
    conn.close()

    # Сохраняем в лог и отчёт
    log_and_report_translation(
        source_text, translated_text, source_language, target_language, translation_date
    )


def get_translation_history():
    """Получаем историю переводов."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT th.id, t.source_text, t.translated_text, th.source_language, th.target_language, th.translation_date
                      FROM translation_history th
                      JOIN translations t ON th.translation_id = t.id"""
    )

    history = cursor.fetchall()
    conn.close()

    return history


# Функция для удаления записи о переводе из базы данных
def delete_translation(translation_id):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        # Выполняем запрос на удаление записи по translation_id
        print(
            f"Attempting to delete record with ID: {translation_id}"
        )  # Выводим для проверки

        c.execute(
            "DELETE FROM translation_history WHERE translation_id = ?",
            (translation_id,),
        )
        c.execute(
            "DELETE FROM translations WHERE id = ?", (translation_id,)
        )  # Удаляем из обеих таблиц

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error occurred while deleting record: {e}")
