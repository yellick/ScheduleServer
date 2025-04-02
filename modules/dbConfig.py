import os

host = os.environ.get('DB_HOST', 'mysql')
login = os.environ.get('MYSQL_USER', 'root')
password = os.environ.get('MYSQL_PASSWORD', '')
db = os.environ.get('MYSQL_DATABASE', 'schdb')
port = int(os.environ.get('DB_PORT', 3306))