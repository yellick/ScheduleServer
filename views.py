from flask import request, jsonify
from modules.SQLModules import SQL


def check_connection():
    response = SQL.check_connection().to_dict()
    return jsonify(response)

def auth():
    try:
        data = request.get_json()
        login = data.get('login')
        password = data.get('password')

        response = SQL.auth(login, password)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500

def check_user():
    try:
        data = request.get_json()
        user_id = data.get('u_id')

        response = SQL.check_user(user_id)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500

def get_themes():    
    try:
        data = request.get_json()
        user_id = data.get('u_id')
        
        response = SQL.get_themes(user_id)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500
    
def get_skipping():
    try:
        data = request.get_json()
        user_id = data.get('u_id')
        
        response = SQL.get_skipping(user_id)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500

def get_schedule():
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        
        response = SQL.get_schedule(group_id)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500

def get_groups():
    response = SQL.get_groups().to_dict()
    return jsonify(response)

def update_groups():
    try:
        data = request.get_json()
        user_id = data.get('u_id')
        
        response = SQL.update_groups(user_id)
        return jsonify(response.to_dict())
    except Exception as e:
        return jsonify({
            "code": -1,
            "status": "Internal server error",
            "response": {"error": str(e)}
        }), 500
