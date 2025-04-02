from flask import Flask
from flask_cors import CORS
from views import *

app = Flask(__name__)
CORS(app)

app.route('/check_connection', methods=['GET', 'POST'])(check_connection)
app.route('/get_user_data', methods=['POST', 'GET'])(get_user_data)
app.route('/get_schedule', methods=['POST', 'GET'])(get_schedule)
app.route('/start_session', methods=['POST', 'GET'])(start_session)
app.route('/check_session', methods=['POST', 'GET'])(check_session)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000

    app.run(host=host, port=port)