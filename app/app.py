import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for
from googletrans import Translator
from app.database import (
    init_db,
    save_translation,
    get_translation_history,
    delete_translation,
)

# Инициализация переводчика
translator = Translator()

# Создаем директории для логов и отчетов
os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Настройка логирования
log_file_path = os.path.join("logs", "log.log")
handler = RotatingFileHandler(log_file_path, maxBytes=100000, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Функция для логирования и записи в отчет
def log_and_report_translation(original, translated, src, tgt, date):
    logging.info(f'Перевод: "{original}" → "{translated}" ({src} → {tgt}) [{date}]')
    report_path = os.path.join("reports", "report.html")
    if not os.path.exists(report_path):
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                '<html><head><meta charset="UTF-8"><title>Отчёт о переводах</title></head><body><h1>История переводов</h1>'
            )
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(
            f'<p><strong>{date}</strong>: "{original}" → <em>"{translated}"</em> '
            f"({LANGUAGES_RU.get(src, src)} → {LANGUAGES_RU.get(tgt, tgt)})</p>\n"
        )


# Создаем приложение с правильными путями к шаблонам и статике
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
)

# Инициализация базы данных при запуске приложения
init_db()

# Словарь языков для отображения на русском
LANGUAGES_RU = {
    "en": "Английский",
    "af": "Африкаанс",
    "sq": "Албанский",
    "am": "Амхарский",
    "ar": "Арабский",
    "hy": "Армянский",
    "az": "Азербайджанский",
    "eu": "Баскский",
    "be": "Белорусский",
    "bn": "Бенгальский",
    "bs": "Боснийский",
    "bg": "Болгарский",
    "ca": "Каталанский",
    "ceb": "Себуано",
    "ny": "Чичева",
    "zh-cn": "Китайский (упрощённый)",
    "zh-tw": "Китайский (традиционный)",
    "co": "Корсиканский",
    "hr": "Хорватский",
    "cs": "Чешский",
    "da": "Датский",
    "nl": "Голландский",
    "eo": "Эсперанто",
    "et": "Эстонский",
    "tl": "Филиппинский",
    "fi": "Финский",
    "fr": "Французский",
    "gl": "Галисийский",
    "ka": "Грузинский",
    "de": "Немецкий",
    "el": "Греческий",
    "gu": "Гуджарати",
    "ht": "Гаитянский",
    "ha": "Хауса",
    "haw": "Гавайский",
    "iw": "Иврит",
    "hi": "Хинди",
    "hmn": "Хмонг",
    "hu": "Венгерский",
    "is": "Исландский",
    "ig": "Игбо",
    "id": "Индонезийский",
    "ga": "Ирландский",
    "it": "Итальянский",
    "ja": "Японский",
    "jw": "Яванский",
    "kn": "Каннада",
    "kk": "Казахский",
    "km": "Кхмерский",
    "ko": "Корейский",
    "ku": "Курдский",
    "ky": "Киргизский",
    "lo": "Лаосский",
    "la": "Латынь",
    "lv": "Латышский",
    "lt": "Литовский",
    "lb": "Люксембургский",
    "mk": "Македонский",
    "mg": "Малагасийский",
    "ms": "Малайский",
    "ml": "Малаялам",
    "mt": "Мальтийский",
    "mi": "Маори",
    "mr": "Маратхи",
    "mn": "Монгольский",
    "my": "Бирманский",
    "ne": "Непальский",
    "no": "Норвежский",
    "ps": "Пушту",
    "fa": "Персидский",
    "pl": "Польский",
    "pt": "Португальский",
    "pa": "Панджаби",
    "ro": "Румынский",
    "ru": "Русский",
    "sm": "Самоанский",
    "gd": "Шотландский (гэльский)",
    "sr": "Сербский",
    "st": "Сесото",
    "sn": "Шона",
    "sd": "Синдхи",
    "si": "Сингальский",
    "sk": "Словацкий",
    "sl": "Словенский",
    "so": "Сомалийский",
    "es": "Испанский",
    "su": "Сунданский",
    "sw": "Суахили",
    "sv": "Шведский",
    "tg": "Таджикский",
    "ta": "Тамильский",
    "te": "Телугу",
    "th": "Тайский",
    "tr": "Турецкий",
    "uk": "Украинский",
    "ur": "Урду",
    "uz": "Узбекский",
    "vi": "Вьетнамский",
    "cy": "Валлийский",
    "xh": "Коса",
    "yi": "Идиш",
    "yo": "Йоруба",
    "zu": "Зулу",
}


@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = None
    if request.method == "POST":
        text = request.form["text"]
        src_lang = request.form["source_language"]
        tgt_lang = request.form["target_language"]

        translated = translator.translate(text, src=src_lang, dest=tgt_lang)
        translated_text = translated.text

        translation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_translation(text, translated_text, src_lang, tgt_lang, translation_date)
        log_and_report_translation(
            text, translated_text, src_lang, tgt_lang, translation_date
        )

    return render_template(
        "index.html", available_languages=LANGUAGES_RU, translated_text=translated_text
    )


@app.route("/delete_history/<int:translation_id>", methods=["GET"])
def delete_history(translation_id):
    try:
        delete_translation(translation_id)  # Удаляем запись из базы данных
        return redirect(
            url_for("history")
        )  # Перенаправляем на страницу с историей переводов
    except Exception as e:
        print(f"Error occurred: {e}")
        return redirect(url_for("history"))


@app.route("/history")
def history():
    history_entries = get_translation_history()
    return render_template("history.html", history=history_entries)


if __name__ == "__main__":
    app.run(debug=True)
