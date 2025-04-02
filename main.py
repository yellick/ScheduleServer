from flask import Flask, jsonify
from flask_cors import CORS
#from views import *

app = Flask(__name__)
CORS(app)

#app.route('/check_connection', methods=['POST'])(check_connection)
#app.route('/get_user_data', methods=['POST'])(get_user_data)
#app.route('/get_schedule', methods=['POST'])(get_schedule)
#app.route('/start_session', methods=['POST'])(start_session)
#app.route('/check_session', methods=['POST'])(check_session)

@app.route('/check_connection', methods=['GET'])
def check_connection():
    import os

    host = os.environ.get('DB_HOST', 'mysql')
    login = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    db = os.environ.get('MYSQL_DATABASE', 'schdb')
    port = int(os.environ.get('DB_PORT', 3306))

    response = {
        'host': host,
        'login': login,
        'pass': password,
        'db': db,
        'port': port
    }
    return jsonify(response)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000

    app.run(host=host, port=port)