import sys
import os
import sqlite3
import pytest

# Добавляем путь к папке, где находится app/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import app
from app.database import init_db, save_translation, get_all_translations


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_database_connection():
    init_db()
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    assert ("translations",) in tables


def test_save_and_retrieve_translation():
    init_db()
    save_translation("Hello", "Привет")
    translations = get_all_translations()
    assert any(t[1] == "Hello" and t[2] == "Привет" for t in translations)


def test_flask_app(client):
    response = client.post("/translate", data={"text": "Hello", "target_lang": "ru"})
    assert response.status_code == 200
    assert "Привет" in response.get_data(as_text=True)
