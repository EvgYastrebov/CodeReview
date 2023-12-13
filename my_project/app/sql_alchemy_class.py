from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

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
    stats = relationship("Stats", backref="match", lazy="dynamic")

class Stats(Base):
    __tablename__ = 'MatchStats'
    EMPLOYEE_ID = Column(Integer, primary_key=True)
    player = Column(String)
    h_a = Column(String)
    shots = Column(Integer)
    goals = Column(Integer)
    xg = Column(Float)
    key_passes = Column(Integer)
    assists = Column(Integer)
    xa = Column(Float)
    match_id = Column(Integer, ForeignKey('Matches.match_id'))