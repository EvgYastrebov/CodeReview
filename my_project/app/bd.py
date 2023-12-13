import psycopg2
from sql_alchemy_class import Match, Stats
from scrap import GetData
from config import database, user, password, host, EPL_tour_less_4, EPL_other, La_liga, Bundesliga, Serie_A, Ligue_1, RPL, EPL_count_of_matches, La_liga_count_of_matches, Bundesliga_count_of_matches, Serie_A_count_of_matches, Ligue_1_count_of_matches, RPL_count_of_matches

def CreateTables():
    conn = psycopg2.connect(database = database, user = user, password = password, host = host)
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
        EMPLOYEE_ID SERIAL PRIMARY KEY,
        player VARCHAR(255),
        h_a VARCHAR(255),
        shots INTEGER,
        goals INTEGER,
        xg REAL,
        key_passes INTEGER,
        assists INTEGER,
        xa REAL,
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
        AddMatch(data, elem, session)

def AddMatch(data, match_id, session):
    match = Match(match_id = match_id, h_team = data['match']['h_team'], h_goals = data['match']['h_goals'], h_xg = data['match']['h_xg'], a_team = data['match']['a_team'], a_goals = data['match']['a_goals'], a_xg = data['match']['a_xg'])
    session.add(match)

    for h_a in ['h', 'a']:
        for i in range(len(data[h_a])):
            shot = Stats(player = data[h_a][i]['player'],
                         h_a = 'h' if h_a == 'h' else 'a',
                         shots = data[h_a][i]['shots'],
                         goals = data[h_a][i]['goals'],
                         xg = data[h_a][i]['xg'],
                         key_passes = data[h_a][i]['key_passes'],
                         assists = data[h_a][i]['assists'],
                         xa = data[h_a][i]['xa'],
                         match_id = match_id)
            session.add(shot)
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
    match_stats = match.stats.all()
    return FilterStat(match, match_stats)

#получить отчет по туру
def GetReportOnTour(tournament, tour, session):
    matches_id = GetMatchesId(tournament, tour)
    report_data = {'shots' : [], 'xg' : [], 'xa': []}
    for match_id in matches_id:
        match = session.query(Match).filter_by(match_id = match_id).first()
        players_stat = match.stats.all()
        for player_stat in players_stat:
            if (4 < player_stat.shots):
                if player_stat.h_a == 'h':
                    report_data['shots'].append({'name' : player_stat.player, 'team' : match.h_team, 'shots': player_stat.shots})
                else:
                    report_data['shots'].append({'name' : player_stat.player, 'team' : match.a_team, 'shots': player_stat.shots})    
            elif (0.6 < player_stat.xg):
                if player_stat.h_a == 'h':
                    report_data['xg'].append({'name' : player_stat.player, 'team' : match.h_team, 'xg' : player_stat.xg})
                else:
                    report_data['xg'].append({'name' : player_stat.player, 'team' : match.a_team, 'xg': player_stat.xg})    
            elif (0.6 < player_stat.xa):
                if player_stat.h_a == 'h':
                    report_data['xa'].append({'name' : player_stat.player, 'team' : match.h_team, 'xa' : player_stat.xa})
                else:
                    report_data['xa'].append({'name' : player_stat.player, 'team' : match.a_team, 'xa': player_stat.xa})    
    report_data['shots'].sort(key=lambda x: x['shots'], reverse=True)
    report_data['xg'].sort(key=lambda x: x['xg'], reverse=True)
    report_data['xa'].sort(key=lambda x: x['xa'], reverse=True)
    return report_data

#отфильтровать игроков, которые имели большой шанс совершить результативное действие
def FilterStat(match, players_stat):
    report_stats = {'match': [], 'h': [], 'a': []}
    report_stats['match'].append({'h_team' : match.h_team, 'h_goals' : match.h_goals, 'h_xg' : f"{match.h_xg:.2f}", 'a_xg' : f"{match.a_xg:.2f}", 'a_goals' : match.a_goals, 'a_team' : match.a_team})
    for player_stat in players_stat:
        if (0.5 <= player_stat.xg + player_stat.xa or 0 < player_stat.goals or 0 < player_stat.assists):
            report_stats[player_stat.h_a].append({'name' : player_stat.player, 'shots': player_stat.shots, 'xg' : player_stat.xg, 'goals' : player_stat.goals, 'key_passes' : player_stat.key_passes, 'xa' : player_stat.xa, 'assists' : player_stat.assists})
    return report_stats

#получить id матчей тура
def GetMatchesId(tournament, tour):
    matches_id = []
    if tournament == 'EPL':
        if tour <= 3:
            for match_id in range(EPL_tour_less_4 + (tour - 1) * EPL_count_of_matches, EPL_tour_less_4 + tour * EPL_count_of_matches):
                matches_id.append(match_id)
        else:
            for match_id in range(EPL_other + (tour - 4) * EPL_count_of_matches, EPL_other + (tour - 3) * EPL_count_of_matches):
                matches_id.append(match_id)
    elif tournament == 'La_liga':
        for match_id in range(La_liga + (tour - 1) * La_liga_count_of_matches, La_liga + tour * La_liga_count_of_matches):
            matches_id.append(match_id)
    elif tournament == 'Bundesliga':
        for match_id in range(Bundesliga + (tour - 1) * Bundesliga_count_of_matches, Bundesliga + tour * Bundesliga_count_of_matches):
            matches_id.append(match_id )
    elif tournament == 'Serie_A':
        for match_id in range(Serie_A + (tour - 1) * Serie_A_count_of_matches, Serie_A + tour * Serie_A_count_of_matches):
            matches_id.append(match_id)
    elif tournament == 'Ligue_1':
        for match_id in range(Ligue_1 + (tour - 1) * Ligue_1_count_of_matches, Ligue_1 + tour * Ligue_1_count_of_matches):
            matches_id.append(match_id)
    elif tournament == 'RPL':
        for match_id in range(RPL + (tour - 1) * RPL_count_of_matches, RPL + tour * RPL_count_of_matches):
            matches_id.append(match_id)
    return matches_id