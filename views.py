from flask import request, jsonify
from modules.SQLModules import SQL
from modules.parcer import Parser


def check_connection():
    response = SQL.check_connection().to_dict()
    return jsonify(response)


def get_user_data():
    parser = Parser()
    try:
        response = parser.get_user_data("22201003", "xDW8Nzmf")
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_user_data1():
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