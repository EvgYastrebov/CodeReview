from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def GetData(match_id):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://understat.com/match/{match_id}')
    driver.implicitly_wait(10)

    html_h = driver.execute_script("return document.body.innerHTML")

    element = driver.find_element(By.CSS_SELECTOR, 'label[for="team-away"]')
    element.click()
    html_a = driver.execute_script("return document.body.innerHTML")
    driver.close()

    data = {'match': '', 'h': '', 'a': ''}
    #найти статистику домашней команды
    bsObj_h = BeautifulSoup(html_h, 'html.parser')
    table_h = bsObj_h.find_all('tr')
    data_h = table_h[1:-1]
    data['h'] = (AddPlayerData(data_h))
    
    #найти статистику гостевой команды
    bsObj_a = BeautifulSoup(html_a, 'html.parser')
    table_a = bsObj_a.find_all('tr')
    data_a = table_a[1:-1]
    data['a'] = (AddPlayerData(data_a))

    #найти информацию о командах
    head_table = bsObj_h.find('span', class_='block-match-result')
    team_names = head_table.find_all('a')
    h_team = team_names[0].text
    a_team = team_names[1].text
    match_data_h = table_h[-1].find_all('td')
    h_goals = match_data_h[5].text.strip()
    h_xg = match_data_h[8].text.strip()[:4]
    match_data_a = table_a[-1].find_all('td')
    a_goals = match_data_a[5].text.strip()
    a_xg = match_data_a[8].text.strip()[:4]
    data['match'] = ({'h_team' : h_team, 'h_goals' : h_goals, 'h_xg' : h_xg, 'a_team' : a_team, 'a_goals' : a_goals, 'a_xg' : a_xg})
    return data

def AddPlayerData(data):
    player_data = []
    for row in data:
        columns = row.find_all('td')
        name = columns[1].text.strip()
        shots = columns[4].text.strip()
        goals = columns[5].text.strip()
        key_passes = columns[6].text.strip()
        assists = columns[7].text.strip()
        xg = columns[8].text.strip()[:4]
        xa = columns[9].text.strip()[:4]
        player_data.append({'player' : name, 'shots' : shots, 'xg' : xg, 'goals' : goals, 'key_passes' : key_passes, 'xa' : xa, 'assists' : assists})    
    return player_data