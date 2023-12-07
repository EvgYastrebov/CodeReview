from pip._vendor import requests
from bs4 import BeautifulSoup
import json

def GetData(match_id):
    print(match_id)
    base_url = 'https://understat.com/match/'
    url = base_url + str(match_id)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    scripts = soup.find_all('script')
    
    content = scripts[1].string
    index_start = content.index("('") + 2
    index_end = content.index("')")
    json_data = content[index_start : index_end].encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)
    return data