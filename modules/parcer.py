import requests
from bs4 import BeautifulSoup

class Parser:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://moodle.preco.ru"
        self.urls = {
            'login': f"{self.base_url}/login/index.php",
            'profile': f"{self.base_url}/user/profile.php",
            'themes': f"{self.base_url}/blocks/lkstudents/themework.php",
            'skipping': f"{self.base_url}/blocks/lkstudents/missedclass.php"
        }

    def moodle_login(self, username, password):
        """Авторизация на Moodle"""
        try:
            response = self.session.get(self.urls['login'])
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'logintoken'})['value'] if soup.find(
                'input', {'name': 'logintoken'}) else ''

            login_data = {
                'username': username,
                'password': password,
                'logintoken': csrf_token
            }
            response = self.session.post(self.urls['login'], data=login_data)
            return (0, "success") if "login/index.php" not in response.url else (1, "Invalid login or password")
        except Exception as e:
            return (1, f"Login error: {str(e)}")

    def get_user_data(self, username, password):
        """Получение данных пользователя"""
        code, msg = self.moodle_login(username, password)
        if code != 0:
            return (code, msg)

        try:
            response = self.session.get(self.urls['profile'])
            soup = BeautifulSoup(response.text, 'html.parser')
            
            full_name = soup.find('h1', {'class': 'h2'})
            email = soup.find('dt', string="Адрес электронной почты")
            
            if not full_name or not email:
                return (1, "User data not found")
            
            return (0, {
                'full_name': full_name.text.strip(),
                'email': email.find_next('dd').find('a').text.strip()
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
            for row in table.find_all('tr')[1:]:  # Пропускаем заголовок
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

    def get_skipping(self, username, password):
        """Получение данных о пропусках"""
        code, msg = self.moodle_login(username, password)
        if code != 0:
            return (code, msg)

        try:
            response = self.session.get(self.urls['skipping'])
            soup = BeautifulSoup(response.text, 'html.parser')

            skipping_data = []
            
            year_containers = soup.find_all('ul', class_='ul_missed_container')
            
            for year_container in year_containers:
                year_div = year_container.find('div', class_='li_div_expand')
                if not year_div:
                    continue
                
                year_text = year_div.get_text(strip=True)
                
                if not year_text.isdigit():
                    continue
                
                year_data = {
                    'year': year_text,
                    'skippings': []
                }
                
                month_containers = year_container.find_all('li', class_='li_missed_node')
                
                for month_container in month_containers:
                    month_div = month_container.find('div', class_='li_div_expand')
                    if not month_div:
                        continue
                    
                    month_text = month_div.get_text(strip=True)
                    
                    if not month_text.isalpha():
                        continue
                    
                    month_data = {
                        'month': month_text,
                        'skipping_days': []
                    }
                    
                    table = month_container.find('table', class_='generaltable')
                    if table:
                        rows = table.select('tbody tr:not(.lastrow)')
                        
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) < 2:
                                continue
                                
                            date_str = cells[0].get_text(strip=True)
                            hours_str = cells[1].get_text(strip=True)
                            
                            try:
                                day = int(date_str.split()[0])
                                hours = int(hours_str) if hours_str.isdigit() else 0
                            except (ValueError, IndexError):
                                continue
                                
                            month_data['skipping_days'].append({
                                'day': day,
                                'hours': hours
                            })
                    
                    year_data['skippings'].append(month_data)
                
                skipping_data.append(year_data)

            return (0, {'skipping': skipping_data}) if skipping_data else (1, "No skipping data found")

        except Exception as e:
            return (1, f"Skipping data retrieval error: {str(e)}")