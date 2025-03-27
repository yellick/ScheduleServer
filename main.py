from flask import Flask
from flask_cors import CORS
from views import *
from modules import SQLModules


app = Flask(__name__)
CORS(app)

# Регистрация маршрутов
app.route('/check_connection', methods=['POST'])(check_connection)
app.route('/get_user_data', methods=['POST'])(get_user_data)
app.route('/get_schedule', methods=['POST'])(get_schedule)
app.route('/start_session', methods=['POST'])(start_session)
app.route('/check_session', methods=['POST'])(check_session)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
