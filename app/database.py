import sqlite3
import os
from datetime import datetime

# Абсолютные пути
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "translations.db")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "log.log")
REPORT_FILE_PATH = os.path.join(REPORTS_DIR, "report.html")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def create_connection(db_path=DATABASE_PATH):
    """Создаём соединение с базой данных."""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def init_db(conn=None):
    """Инициализация базы данных, создание таблиц."""
    created_here = False
    if conn is None:
        conn = create_connection()
        created_here = True

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text TEXT NOT NULL,
            translated_text TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS translation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_id INTEGER NOT NULL,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            translation_date TEXT NOT NULL,
            FOREIGN KEY (translation_id) REFERENCES translations(id)
        )
    """
    )

    conn.commit()
    if created_here:
        conn.close()


def log_and_report_translation(
    source_text, translated_text, source_language, target_language, translation_date
):
    """Сохраняет лог и HTML-отчёт."""
    log_entry = f"[{translation_date}] Перевод: '{source_text}' ({source_language}) → '{translated_text}' ({target_language})\n"
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    html_entry = f"<tr><td>{translation_date}</td><td>{source_language}</td><td>{target_language}</td><td>{source_text}</td><td>{translated_text}</td></tr>\n"
    if not os.path.exists(REPORT_FILE_PATH):
        with open(REPORT_FILE_PATH, "w", encoding="utf-8") as report_file:
            report_file.write(
                """
                <html>
                <head><meta charset='utf-8'><title>Отчёт переводов</title>
                <style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ddd; padding: 8px; } th { background-color: #f2f2f2; }</style>
                </head>
                <body><h2>История переводов</h2><table>
                <tr><th>Дата</th><th>Язык источника</th><th>Язык перевода</th><th>Оригинал</th><th>Перевод</th></tr>
            """
            )

    with open(REPORT_FILE_PATH, "a", encoding="utf-8") as report_file:
        report_file.write(html_entry)


def save_translation(
    source_text,
    translated_text,
    source_language,
    target_language,
    translation_date,
    conn=None,
):
    """Сохраняем перевод в базу и логируем."""
    created_here = False
    if conn is None:
        conn = create_connection()
        created_here = True

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO translations (source_text, translated_text) VALUES (?, ?)",
        (source_text, translated_text),
    )
    translation_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO translation_history (translation_id, source_language, target_language, translation_date)
        VALUES (?, ?, ?, ?)
    """,
        (translation_id, source_language, target_language, translation_date),
    )

    conn.commit()
    if created_here:
        conn.close()

    log_and_report_translation(
        source_text, translated_text, source_language, target_language, translation_date
    )


def get_translation_history(conn=None):
    """Получаем историю переводов."""
    created_here = False
    if conn is None:
        conn = create_connection()
        created_here = True

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT th.id, t.source_text, t.translated_text,
               th.source_language, th.target_language, th.translation_date
        FROM translation_history th
        JOIN translations t ON th.translation_id = t.id
    """
    )
    history = cursor.fetchall()

    if created_here:
        conn.close()

    return history


def delete_translation(translation_id, conn=None):
    """Удаляем перевод из базы данных."""
    created_here = False
    if conn is None:
        conn = create_connection()
        created_here = True

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM translation_history WHERE translation_id = ?", (translation_id,)
    )
    cursor.execute("DELETE FROM translations WHERE id = ?", (translation_id,))

    conn.commit()
    if created_here:
        conn.close()
