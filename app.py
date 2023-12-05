# # from flask import Flask, request, redirect, url_for
# # from flask_sqlalchemy import SQLAlchemy
# # import random
# # from datetime import datetime
# #
# #
# # app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# #
# # db = SQLAlchemy(app)
# #
# # @app.before_request
# # def before_first_request():
# #     if not hasattr(app, 'urls_created'):
# #         app.urls_created = True
# #         create_tables()
# #
# # def create_tables():
# #     db.create_all()
# #
# # class Urls(db.Model):
# #     id_ = db.Column("id_", db.Integer, primary_key=True)
# #     long = db.Column("long", db.String())
# #     short = db.Column("short", db.String(10), unique=True)
# #     stats = db.relationship('UrlStats', backref='url', lazy=True)  # Связь с таблицей статистики
# #
# #     def __init__(self, long, short):
# #         self.long = long
# #         self.short = short
# #
# # class UrlStats(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     url_id = db.Column(db.Integer, db.ForeignKey('urls.id_'), nullable=False)
# #     ip_address = db.Column(db.String(15))
# #     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
# #
# # def shorten_url(long_url):
# #     existing_url = Urls.query.filter_by(long=long_url).first()
# #     if existing_url:
# #         return existing_url.short
# #     else:
# #         letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# #         rand_letters = "".join(random.choices(letters, k=3))
# #         short_url = rand_letters
# #
# #         new_url = Urls(long=long_url, short=short_url)
# #         db.session.add(new_url)
# #         db.session.commit()
# #
# #         return short_url
# #
# # @app.route('/', methods=['POST', 'GET'])
# # def home():
# #     if request.method == "POST":
# #         url_received = request.form["nm"]
# #         short_url = shorten_url(url_received)
# #
# #         # Добавим запись в статистику при переходе по сокращенной ссылке
# #         ip_address = request.remote_addr
# #         url_stats = UrlStats(ip_address=ip_address, url_id=new_url.id_)
# #         db.session.add(url_stats)
# #         db.session.commit()
# #
# #         return f'http://127.0.0.1:5000/{short_url}'
# #     else:
# #         return 'This is a simple URL shortener.'
# #
# # @app.route('/<short_url>')
# # def redirection(short_url):
# #     long_url = Urls.query.filter_by(short=short_url).first()
# #     if long_url:
# #         # Добавим запись в статистику при переходе по сокращенной ссылке
# #         ip_address = request.remote_addr
# #         url_stats = UrlStats(ip_address=ip_address, url_id=long_url.id_)
# #         db.session.add(url_stats)
# #         db.session.commit()
# #
# #         return redirect(long_url.long)
# #     else:
# #         return 'URL not found.'
# #
# # if __name__ == '__main__':
# #     app.run(port=5000, debug=True)
#
#
# from flask import Flask, request, redirect, render_template, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from models import db, ClickStats, Urls  # Импортируйте новую модель
# from datetime import datetime, timedelta
# import random
# import json
# from sqlalchemy import func
#
#
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db.init_app(app)
#
# report = "report.json"
#
# @app.before_request
# def before_first_request():
#     if not hasattr(app, 'urls_created'):
#         app.urls_created = True
#         create_tables()
#
# def create_tables():
#     with app.app_context():  # Оборачиваем создание таблиц в контекст приложения
#         db.create_all()
#
# # class Urls(db.Model):
# #     id_ = db.Column("id_", db.Integer, primary_key=True)
# #     long = db.Column("long", db.String())
# #     short = db.Column("short", db.String(10), unique=True)
# #     clicks = db.Column("clicks", db.Integer, default=0)  # Новое поле для отслеживания переходов
# #
# #     def __init__(self, long, short):
# #         self.long = long
# #         self.short = short
#
# def shorten_url(long_url):
#     existing_url = Urls.query.filter_by(long=long_url).first()
#     if existing_url:
#         return existing_url.short
#     else:
#         # Если такой длинной ссылки нет, генерируем и сохраняем новую короткую ссылку
#         letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
#         rand_letters = "".join(random.choices(letters, k=3))
#         short_url = rand_letters
#
#         new_url = Urls(long=long_url, short=short_url)
#         db.session.add(new_url)
#         db.session.commit()
#
#         return short_url
#
# @app.route('/', methods=['POST', 'GET'])
# def home():
#     short_url = None
#     if request.method == "POST":
#         url_received = request.form["nm"]
#         short_url = shorten_url(url_received)
#     return render_template('home.html', short_url=short_url)
#
# @app.route('/<short_url>')
# def redirection(short_url):
#     long_url = Urls.query.filter_by(short=short_url).first()
#     if long_url:
#         return redirect(long_url.long)
#     else:
#         return 'URL not found.'
#
# @app.route('/stats/<short_url>')
# def stats(short_url):
#     clicks = ClickStats.query.filter_by(short_url=short_url).all()
#     return render_template('stats.html', clicks=clicks)
#
# def generate_report_data():
#     details_order = request.args.get('details_order', default=[], type=list)
#
#     # Подготовим структуру данных для отчета
#     report_data = []
#     parent_map = {}
#
#     # Функция для добавления записи в отчет
#     def add_to_report(parent_id, url, source_ip, time_interval, count):
#         report_data.append({
#             "Id": len(report_data) + 1,
#             "Pid": parent_id,
#             "URL": url,
#             "SourceIP": source_ip,
#             "TimeInterval": time_interval,
#             "Count": count
#         })
#
#     # Функция для обработки уровней детализации
#     def process_details_level(data, details_order, parent_id=None):
#         if not details_order:
#             return
#
#         current_detail = details_order[0]
#         remaining_details = details_order[1:]
#
#         if current_detail == "SourceIP":
#             unique_source_ips = set([item["source_ip"] for item in data])
#             for source_ip in unique_source_ips:
#                 add_to_report(parent_id, None, source_ip, None, sum(item["count"] for item in data if item["source_ip"] == source_ip))
#                 child_id = len(report_data)
#                 process_details_level([item for item in data if item["source_ip"] == source_ip], remaining_details, child_id)
#
#         elif current_detail == "TimeInterval":
#             unique_time_intervals = set([item["time_interval"] for item in data])
#             for time_interval in unique_time_intervals:
#                 add_to_report(parent_id, None, None, time_interval, sum(item["count"] for item in data if item["time_interval"] == time_interval))
#                 child_id = len(report_data)
#                 process_details_level([item for item in data if item["time_interval"] == time_interval], remaining_details, child_id)
#
#         elif current_detail == "URL":
#             unique_urls = set([item["url"] for item in data])
#             for url in unique_urls:
#                 add_to_report(parent_id, url, None, None, sum(item["count"] for item in data if item["url"] == url))
#
#     # Запрос данных из базы данных
#     click_stats = ClickStats.query.all()
#     for stat in click_stats:
#         long_url = Urls.query.filter_by(short=stat.short_url).first()
#         url = f"{long_url.long} ({stat.short_url})"
#         source_ip = stat.source_ip
#         timestamp = stat.timestamp
#         time_interval = timestamp.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Обновляем или создаем запись в отчете
#         if url not in parent_map:
#             parent_map[url] = len(report_data) + 1
#             add_to_report(None, url, None, None, stat.count)
#         else:
#             report_data[parent_map[url] - 1]["Count"] += stat.count
#
#         add_to_report(parent_map[url], None, source_ip, time_interval, stat.count)
#
#     # Генерируем отчет
#     process_details_level(report_data, details_order)
#
#     # Записываем отчет в файл JSON
#     with open(report, 'w') as file:
#         json.dump(report_data, file, indent=2)
#
#     return report_data
#
# @app.route('/report', methods=['GET'])
# def generate_report():
#     report_data = generate_report_data()
#     return jsonify(report_data)
#
# @app.route('/collect_stats', methods=['GET'])
# def collect_stats():
#     # Сначала собираем статистику в базе данных
#     generate_report_data()
#
#     # Затем получаем её из базы для записи в файл
#     report_data = ClickStats.query.all()
#
#     # Записываем отчет в файл JSON
#     with open(report, 'w') as file:
#         json.dump(report_data, file, indent=2)
#
#     return jsonify(report_data)
#
# if __name__ == '__main__':
#     app.run(port=5000, debug=True)





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


