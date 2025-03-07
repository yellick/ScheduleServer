from flask import request, jsonify
from modules.SQLModules import SQL


def check_connection():
    response = True#SQL.chec_connection().to_dict()
    return jsonify(response)

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