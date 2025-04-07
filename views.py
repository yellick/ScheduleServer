from flask import request, jsonify
from modules.SQLModules import SQL
import os

###################################
login = os.environ.get('TEST_USER')
password = os.environ.get('TEST_PASSWORD')
###################################


def check_connection():
    response = SQL.check_connection().to_dict()
    return jsonify(response)

def auth():
    print(login)
    print(password)
    
    try:
        response = SQL.auth(login, password)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500

def get_user_data():
    data = request.get_json()
    user_id = data.get('user_id')

    response = SQL.get_user_data_by_id(user_id).to_dict()
    return jsonify(response)

def get_schedule():
    data = request.get_json()
    group_id = data.get('group_id')

    response = SQL.get_schedule_by_group(group_id).to_dict()
    return jsonify(response)

def start_session():
    data = request.get_json()
    user_id = data.get('user_id')

    response = SQL.start_session(user_id).to_dict()
    return jsonify(response)

def check_session():
    data = request.get_json()
    hash = data.get('hash')

    response = SQL.check_session(hash).to_dict()
    return jsonify(response)