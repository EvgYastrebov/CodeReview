import psycopg2
from sql_alchemy_class import Match, Shots
from scrap import GetData

def CreateTables():
    conn = psycopg2.connect(database="data_bace", user="user", password="123", host="postgres")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Matches (
        match_id SERIAL PRIMARY KEY,
        h_team VARCHAR(255),
        h_goals INTEGER,
        h_xg REAL,
        a_team VARCHAR(255),
        a_goals INTEGER,
        a_xg REAL
        )
        ''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS MatchStats (
        shot_id SERIAL PRIMARY KEY,
        result BOOLEAN,
        xg REAL,
        X REAL,
        Y REAL,
        h_a VARCHAR(255),
        player VARCHAR(255),
        player_assisted VARCHAR(255),
        match_id INTEGER,
        FOREIGN KEY(match_id) REFERENCES Matches(match_id)
        )
        ''')
    conn.commit()
    conn.close()

#добавить тур
def InitTour(tournament, tour, session):
    matches_id = GetMatchesId(tournament, tour)
    for elem in matches_id:
        if session.query(Match).filter_by(match_id = elem).first() is not None:
            continue
        data = GetData(elem)
        AddMatch(data, session)

def AddMatch(data, session):
    match = Match(match_id = data['h'][0]['match_id'], h_team = data['h'][0]['h_team'], a_team = data['h'][0]['a_team'])
    session.add(match)

    h_xg = 0
    a_xg = 0
    h_goals = 0
    a_goals = 0
    for h_a in ['h', 'a']:
        for i in range(len(data[h_a])):
            if h_a == 'h':
                h_xg += float(data[h_a][i]['xG'])
                if data[h_a][i]['result'] == 'Goal':
                    h_goals += 1 
            else:
                a_xg += float(data[h_a][i]['xG'])
                if data[h_a][i]['result'] == 'Goal':
                    a_goals += 1
        
            shot = Shots(shot_id = data[h_a][i]['id'],
                         match_id = data[h_a][i]['match_id'],
                         result = 1 if data[h_a][i]['result'] == 'Goal' else 0,
                         xg = data[h_a][i]['xG'],
                         X = data[h_a][i]['X'],
                         Y = data[h_a][i]['Y'],
                         h_a = 'h' if h_a == 'h' else 'a',
                         player = data[h_a][i]['player'],
                         player_assisted = data[h_a][i]['player_assisted'])
            session.add(shot)

    match = session.query(Match).filter(Match.match_id == data['h'][0]['match_id']).first()
    match.h_xg = h_xg
    match.a_xg = a_xg
    match.h_goals = h_goals
    match.a_goals = a_goals
    
    session.commit()

#получить все доступные матчи
def GetAllMatches(session):
    matches_data = {}
    for elem in session.query(Match).all():
        matches_data[elem.match_id] = {'h_team' : elem.h_team, 'h_goals' : elem.h_goals, 'h_xg' : f'{elem.h_xg:.2f}', 'a_team' : elem.a_team, 'a_goals' : elem.a_goals, 'a_xg' : f'{elem.a_xg:.2f}'}
    return matches_data

#получить матчи только выбранного тура
def GetTourMatches(tournament, tour, session):
    matches_id = GetMatchesId(tournament, tour)
    matches_data = {}
    for elem in matches_id:
        match = session.query(Match).filter(Match.match_id == elem).first()
        matches_data[match.match_id] = {'h_team' : match.h_team, 'h_goals' : match.h_goals, 'h_xg' : f'{match.h_xg:.2f}', 'a_team' : match.a_team, 'a_goals' : match.a_goals, 'a_xg' : f'{match.a_xg:.2f}'}
    
    return matches_data

#получить отчет по матчу
def GetReportOnMatch(match_id, session):
    match = session.query(Match).filter_by(match_id = match_id).first()
    match_shots = match.shots.all()
    return FilterStat(match, CountPlayersStat(match_shots))

#получить отчет по туру
def GetReportOnTour(tournament, tour, session):
    matches_id = GetMatchesId(tournament, tour)
    report_data = {'shots' : [], 'xg' : [], 'xa': []}
    for match_id in matches_id:
        match = session.query(Match).filter_by(match_id = match_id).first()
        players_stat = CountPlayersStat(match.shots.all())
        for player, player_stat in players_stat.items():
            if (4 < player_stat['shots']):
                if player_stat['h_a'] == 'h':
                    report_data['shots'].append({'name' : player, 'team' : match.h_team, 'shots': player_stat['shots']})
                else:
                    report_data['shots'].append({'name' : player, 'team' : match.a_team, 'shots': player_stat['shots']})    
            elif (0.6 < player_stat['xg']):
                if player_stat['h_a'] == 'h':
                    report_data['xg'].append({'name' : player, 'team' : match.h_team, 'xg' : f"{player_stat['xg']:.2f}"})
                else:
                    report_data['xg'].append({'name' : player, 'team' : match.a_team, 'xg': f"{player_stat['xg']:.2f}"})    
            elif (0.6 < player_stat['xa']):
                if player_stat['h_a'] == 'h':
                    report_data['xa'].append({'name' : player, 'team' : match.h_team, 'xa' : f"{player_stat['xa']:.2f}"})
                else:
                    report_data['xa'].append({'name' : player, 'team' : match.a_team, 'xa': f"{player_stat['xa']:.2f}"})    
    report_data['shots'].sort(key=lambda x: x['shots'], reverse=True)
    report_data['xg'].sort(key=lambda x: x['xg'], reverse=True)
    report_data['xa'].sort(key=lambda x: x['xa'], reverse=True)
    return report_data

#подсчет статистики для каждого игрока
def CountPlayersStat(match_shots):
    players_stat = {}
    for shot in match_shots:
        if (shot.result or 0.2 <= shot.xg or ((shot.X <= 0.2 or 0.8 <= shot.X) and 0.2 <= shot.Y <= 0.8)):
            if shot.player not in players_stat.keys():
                players_stat[shot.player] = {'h_a' : shot.h_a, 'shots': 1, 'xg' : shot.xg, 'goals' : 1 if shot.result else 0, 'key_passes' : 0, 'xa' : 0, 'assists' : 0}
                
            else:
                players_stat[shot.player]['shots'] += 1
                players_stat[shot.player]['xg'] += shot.xg
                players_stat[shot.player]['goals'] += 1 if shot.result else 0
            if shot.player_assisted:
                if shot.player_assisted not in players_stat.keys():
                    players_stat[shot.player_assisted] = {'h_a' : shot.h_a, 'shots': 0, 'xg' : 0, 'goals' : 0, 'key_passes' : 1, 'xa' : shot.xg, 'assists' : 1 if shot.result else 0}
                else:
                    players_stat[shot.player_assisted]['key_passes'] += 1
                    players_stat[shot.player_assisted]['xa'] += shot.xg
                    players_stat[shot.player_assisted]['assists'] += 1 if shot.result else 0
    return players_stat

#отфильтровать опасные удары в матче
def FilterStat(match, players_stat):
    report_shots = {'match': [], 'h': [], 'a': []}
    report_shots['match'].append({'h_team' : match.h_team, 'h_goals' : match.h_goals, 'h_xg' : f"{match.h_xg:.2f}", 'a_xg' : f"{match.a_xg:.2f}", 'a_goals' : match.a_goals, 'a_team' : match.a_team})
    for player, player_stat in players_stat.items():
        if (0.4 <= player_stat['xg'] + player_stat['xa'] or 0 < player_stat['goals'] or 0 < player_stat['assists']):
            report_shots[player_stat['h_a']].append({'name' : player, 'shots': player_stat['shots'], 'xg' : f"{player_stat['xg']:.2f}", 'goals' : player_stat['goals'], 'key_passes' : player_stat['key_passes'], 'xa' : f"{player_stat['xa']:.2f}", 'assists' : player_stat['assists']})
    return report_shots

#получить id матчей тура
def GetMatchesId(tournament, tour):
    matches_id = []
    if tournament == 'EPL':
        if tour <= 3:
            for match_id in range(22275 + (tour - 1) * 10, 22275 + tour * 10):
                matches_id.append(match_id)
        else:
            for match_id in range(21925 + (tour - 4) * 10, 21925 + (tour - 3) * 10):
                matches_id.append(match_id)
    elif tournament == 'La_liga':
        for match_id in range(22685 + (tour - 1) * 10, 22685 + tour * 10):
            matches_id.append(match_id)
    elif tournament == 'Bundesliga':
        for match_id in range(23065 + (tour - 1) * 9, 23065 + tour * 9):
            matches_id.append(match_id )
    elif tournament == 'Serie_A':
        for match_id in range(22305 + (tour - 1) * 10, 22305 + tour * 10):
            matches_id.append(match_id)
    elif tournament == 'Ligue_1':
        for match_id in range(23371 + (tour - 1) * 9, 23371 + tour * 9):
            matches_id.append(match_id)
    elif tournament == 'RPL':
        for match_id in range(21685 + (tour - 1) * 8, 21685 + tour * 8):
            matches_id.append(match_id)
    return matches_id