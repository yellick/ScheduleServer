from flask import Flask
from flask_cors import CORS
from views import *
from modules import SQLModules


app = Flask(__name__)
CORS(app)

# Регистрация маршрутов
app.route('/conn_api', methods=['POST'])(check_connection)
app.route('/get_user_data', methods=['POST'])(get_user_data)
app.route('/get_schedule', methods=['POST'])(get_schedule)
app.route('/start_session', methods=['POST'])(start_session)
app.route('/check_session', methods=['POST'])(check_session)

def show_routes(host, port):
    routes = [
        {
            'name': 'Проверка соединения',
            'adress': '/conn_api',
        },
        {
            'name': 'Получить данные пользователя (user_id)',
            'adress': '/get_user_data',
        },
        {
            'name': 'Получить расписание (group_id_',
            'adress': '/get_schedule',
        },
        {
            'name': 'Начать сессию (user_id)',
            'adress': '/start_session',
        },
        {
            'name': 'Проверить сессию (hash)',
            'adress': '/check_session',
        },
    ]

    print(f"Server is running at: http://{host}:{port}\n")
    print("Маршруты: ")

    for i in routes:
        print(f"{i['name']}: http://{host}:{port}{i['adress']}")

    print('\n\n')


if __name__ == '__main__':
    host = 'localhost'
    port = 52703
    
    show_routes(host, port)
    

    app.run(host=host, port=port)
