import requests
from bs4 import BeautifulSoup
import json

class Parser:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://moodle.preco.ru"
        
        self.urls = {
            'login': f"{self.base_url}/login/index.php",
            'schedule': f"{self.base_url}/blocks/lkstudents/sheduleonline.php",
            'themes': f"{self.base_url}/blocks/lkstudents/themework.php",
            'profile': f"{self.base_url}/user/profile.php",
            'skipping': f"{self.base_url}/blocks/lkstudents/missedclass.php"
        }


    def moodle_login(self, username, password):
        try:
            # Шаг 1: Получаем страницу логина
            response = self.session.get(self.urls['login'])
            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем CSRF-токен
            csrf_token = soup.find('input', {'name': 'logintoken'})['value'] if soup.find(
                'input', {'name': 'logintoken'}) else ''

            # Шаг 2: Отправляем POST-запрос
            login_data = {
                'username': username,
                'password': password,
                'logintoken': csrf_token
            }
            response = self.session.post(self.urls['login'], data=login_data)

            return "login/index.php" not in response.url

        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            return False

    
    def get_user_data(self, username, password):
        if not self.moodle_login(username, password):
            return {"error": "Неверный логин или пароль."}

        try:
            response = self.session.get(self.urls['profile'])
            soup = BeautifulSoup(response.text, 'html.parser')

            full_name_tag = soup.find('h1', {'class': 'h2'})
            if not full_name_tag:
                return {"error": "Не удалось найти ФИО пользователя."}
            
            email_tag = soup.find('dt', string="Адрес электронной почты")
            if not email_tag:
                return {"error": "Не удалось найти адрес электронной почты."}

            return {
                "full_name": full_name_tag.text.strip(),
                "email": email_tag.find_next('dd').find('a').text.strip()
            }

        except Exception as e:
            return {"error": str(e)}