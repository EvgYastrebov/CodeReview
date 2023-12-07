from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine  
from sqlalchemy.orm import sessionmaker  
from bd import CreateTables, GetReportOnMatch, GetReportOnTour, InitTour, GetTourMatches, GetAllMatches
from sql_alchemy_class import Base

app = Flask(__name__)
engine = create_engine('sqlite:///data_bace_alch.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/', methods = ['GET'])
def Start():
    CreateTables()
    return redirect(url_for('HandleGetAllMatches'))

@app.route('/add_tour')
def init_page():
    return render_template('init.html')

@app.route('/init', methods=['POST'])
def HandleInit():
    tournament = request.form['tournament'].replace(' ', '_')
    tour = int(request.form['tour'])
    InitTour(tournament, tour, session)
    return redirect(url_for('HandleGetTourMatches', tournament = tournament, tour = tour))

@app.route('/matches/<tournament>/<int:tour>', methods=['GET'])
def HandleGetTourMatches(tournament, tour):
    match_names = GetTourMatches(tournament, tour, session)
    return render_template('matches.html', matches_data = match_names)

@app.route('/matches', methods=['GET'])
def HandleGetAllMatches():
    match_names = GetAllMatches(session)
    if match_names:
        return render_template('matches.html', matches_data = match_names)
    else:
        return "list is empty so far"

@app.route('/report/<int:match_id>', methods=['GET'])
def HandleGetReportOnTour(match_id):
    report = GetReportOnMatch(match_id, session)
    return render_template('report_on_match.html', report = report)

@app.route('/report/<tournament>/<int:tour>', methods=['GET'])
def HandleGetReportOnMatch(tournament, tour):
    tournament = tournament.replace(' ', '_')
    report = GetReportOnTour(tournament, tour, session)
    return render_template('report_on_tour.html', report = report, tour = tour, tournament = tournament)


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8888)