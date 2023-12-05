from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import json
from datetime import datetime

# Создание экземпляра Flask
app = Flask(__name__)

# Конфигурация базы данных SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация объекта SQLAlchemy
db = SQLAlchemy(app)

# Глобальная переменная для хранения статистики переходов по URL
url_stats = []


# Обработчик запроса перед первым запросом
@app.before_request
def before_first_request():
    # Проверка наличия атрибута 'urls_created' в объекте приложения
    if not hasattr(app, 'urls_created'):
        # Установка атрибута 'urls_created' в значение True
        app.urls_created = True
        # Вызов функции для создания таблиц в базе данных
        create_tables()

# Функция для создания таблиц в базе данных
def create_tables():
    # Создание всех таблиц в базе данных, связанных с моделями данных SQLAlchemy
    db.create_all()

# Определение модели данных для таблицы URL
class Urls(db.Model):
    # Определение столбца 'id_' с типом данных Integer, первичным ключом
    id_ = db.Column("id_", db.Integer, primary_key=True)
    # Определение столбца 'long' с типом данных String
    long = db.Column("long", db.String())
    # Определение столбца 'short' с типом данных String, уникальным
    short = db.Column("short", db.String(10), unique=True)

    # Конструктор класса с параметрами 'long' и 'short'
    def __init__(self, long, short):
        self.long = long
        self.short = short

# Функция для сбора статистики по переходам по URL
def collect_stats(url, source_ip):
    # Получение текущего времени в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Поиск существующей статистики по URL и IP-адресу
    existing_stat = next((stat for stat in url_stats if stat['URL'] == url and stat['SourceIP'] == source_ip), None)

    # Если статистика существует, увеличиваем счетчик
    if existing_stat:
        existing_stat['Count'] += 1
    # Иначе добавляем новую запись в статистику
    else:
        url_stats.append({
            'Id': len(url_stats) + 1,
            'Pid': None,
            'URL': url,
            'SourceIP': source_ip,
            'TimeInterval': current_time,
            'Count': 1
        })

# Изменения в функции переадресации
@app.route('/<short_url>')
def redirection(short_url):
    # Получаем длинную ссылку по короткой из базы данных
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        # Собираем статистику при каждом переходе
        collect_stats(long_url.long, request.remote_addr)
        # Перенаправляем на длинную ссылку
        return redirect(long_url.long)
    else:
        # Если ссылка не найдена, возвращаем сообщение
        return 'URL not found.'

# Добавление нового маршрута для генерации отчета
@app.route('/generate_report', methods=['POST'])
def generate_report():
    # Получаем порядок отчета из тела запроса
    report_order = request.json.get('report_order', [])
    # Сортируем статистику по заданному порядку
    sorted_stats = sorted(url_stats, key=lambda x: tuple(x.get(detail, '') for detail in report_order))

    # Запись отчета в JSON файл
    with open('report.json', 'w') as json_file:
        json.dump(sorted_stats, json_file, indent=4)

    # Возвращаем сообщение об успешной генерации отчета
    return 'Report generated successfully!'

# Функция для сокращения URL
def shorten_url(long_url):
    # Проверяем, существует ли такая длинная ссылка в базе данных
    existing_url = Urls.query.filter_by(long=long_url).first()
    if existing_url:
        # Возвращаем существующий короткий URL, если найден
        return existing_url.short
    else:
        # Если такой длинной ссылки нет, генерируем и сохраняем новую короткую ссылку
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rand_letters = "".join(random.choices(letters, k=3))
        short_url = rand_letters

        new_url = Urls(long=long_url, short=short_url)
        db.session.add(new_url)
        db.session.commit()

        return short_url

# Маршрут для домашней страницы
@app.route('/', methods=['POST', 'GET'])
def home():
    short_url = None  # Инициализация переменной short_url
    if request.method == "POST":
        # Получаем URL из формы, сокращаем и передаем в шаблон
        url_received = request.form["nm"]
        short_url = shorten_url(url_received)
    # Отображаем домашнюю страницу с переменной short_url
    return render_template('home.html', short_url=short_url)

# Маршрут для просмотра статистики
@app.route('/view_stats')
def view_stats():
    # Отображаем страницу статистики, передавая статистику в шаблон
    return render_template('stats.html', stats=url_stats)

# Запуск приложения, если файл выполняется как основной скрипт
if __name__ == '__main__':
    # Запускаем приложение на порту 5000 с включенным режимом отладки
    app.run(port=5000, debug=True)


