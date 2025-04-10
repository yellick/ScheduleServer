import requests
from bs4 import BeautifulSoup

class Parser:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://moodle.preco.ru"
        self.urls = {
            'login': f"{self.base_url}/login/index.php",
            'profile': f"{self.base_url}/user/profile.php",
            'themes': f"{self.base_url}/blocks/lkstudents/themework.php"
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

            if "login/index.php" in response.url:
                return (1, "Invalid login or password")
            return (0, "success")

        except Exception as e:
            return (1, f"Login error: {str(e)}")

    def get_user_data(self, username, password):
        login_result = self.moodle_login(username, password)
        if login_result[0] != 0:
            return login_result

        try:
            response = self.session.get(self.urls['profile'])
            soup = BeautifulSoup(response.text, 'html.parser')

            full_name_tag = soup.find('h1', {'class': 'h2'})
            if not full_name_tag:
                return (1, "Failed to find user's full name")
            
            email_tag = soup.find('dt', string="Адрес электронной почты")
            if not email_tag:
                return (1, "Failed to find email address")

            return (0, {
                "full_name": full_name_tag.text.strip(),
                "email": email_tag.find_next('dd').find('a').text.strip()
            })

        except Exception as e:
            return (1, f"Data retrieval error: {str(e)}")
        
    def get_themes(self, username, password):
        """Получение списка тем/работ"""
        code, msg = self.moodle_login(username, password)
        if code != 0:
            return (code, msg)

        try:
            response = self.session.get(self.urls['themes'])
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                return (1, "Themes table not found")

            themes = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    themes.append({
                        'type': cells[0].text.strip(),
                        'theme': cells[1].text.strip(),
                        'curator': cells[2].text.strip()
                    })

            return (0, themes) if themes else (1, "No themes found")
        except Exception as e:
            return (1, f"Themes retrieval error: {str(e)}")