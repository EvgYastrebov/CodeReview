from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Match(Base):
    __tablename__ = 'Matches'
    match_id = Column(Integer, primary_key=True)
    h_team = Column(String)
    h_goals = Column(Integer)
    h_xg = Column(Float)
    a_team = Column(String)
    a_goals = Column(Integer)
    a_xg = Column(Float)
    shots = relationship("Shots", backref="match", lazy="dynamic")

class Shots(Base):
    __tablename__ = 'MatchStats'
    shot_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('Matches.match_id'))
    result = Column(Boolean)
    xg = Column(Float)
    X = Column(Float)
    Y = Column(Float)
    h_a = Column(String)
    player = Column(String)
    player_assisted = Column(String)   
