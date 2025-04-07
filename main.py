from flask import Flask, render_template_string
from flask_cors import CORS
from views import *

app = Flask(__name__)
CORS(app)

# Ваши существующие маршруты
app.route('/check_connection', methods=['GET', 'POST'])(check_connection)
app.route('/get_user_data', methods=['POST', 'GET'])(get_user_data)
app.route('/auth', methods=['POST', 'GET'])(auth)
app.route('/get_schedule', methods=['POST', 'GET'])(get_schedule)
app.route('/start_session', methods=['POST', 'GET'])(start_session)
app.route('/check_session', methods=['POST', 'GET'])(check_session)

# Новый маршрут для индексной страницы
@app.route('/', methods=['GET'])
def index():
    # Собираем информацию о маршрутах
    routes_info = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static' and rule.endpoint != 'index':
            route = {
                'path': rule.rule,
                'methods': ', '.join(method for method in rule.methods if method not in ['OPTIONS', 'HEAD']),
                'endpoint': rule.endpoint
            }
            routes_info.append(route)
    
    # Сортируем маршруты по пути
    routes_info.sort(key=lambda x: x['path'])
    
    # Генерируем HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
            .route { 
                background: #f8f9fa; 
                padding: 15px; 
                margin-bottom: 10px; 
                border-radius: 5px; 
                border-left: 4px solid #4285f4;
            }
            .path { 
                font-weight: bold; 
                color: #4285f4; 
                font-size: 1.1em;
                margin-bottom: 5px;
            }
            .methods { 
                color: #34a853; 
                font-style: italic;
                margin-right: 10px;
            }
            .endpoint { 
                color: #ea4335; 
                font-family: monospace;
            }
            a { 
                text-decoration: none; 
                color: inherit;
            }
            a:hover .path { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>API Endpoints</h1>
        <div class="routes">
            {% for route in routes %}
            <a href="{{ route.path }}">
                <div class="route">
                    <div class="path">{{ route.path }}</div>
                    <div>
                        <span class="methods">{{ route.methods }}</span>
                        <span class="endpoint">{{ route.endpoint }}</span>
                    </div>
                </div>
            </a>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, routes=routes_info)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port)