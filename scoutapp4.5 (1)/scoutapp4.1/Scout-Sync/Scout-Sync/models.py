import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ScoutingSession(Base):
    """A scouting session identified by a team code."""
    __tablename__ = 'scouting_sessions'
    
    id = Column(Integer, primary_key=True)
    team_code = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    pit_scouting = relationship("PitScouting", back_populates="session", cascade="all, delete-orphan")
    match_scores = relationship("MatchScore", back_populates="session", cascade="all, delete-orphan")

class PitScouting(Base):
    """Pit scouting data for an FRC team."""
    __tablename__ = 'pit_scouting'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('scouting_sessions.id'), nullable=False)
    
    frc_team = Column(String(20), nullable=False)
    team_name = Column(String(100))
    drivetrain = Column(String(50))
    robot_weight = Column(Integer)
    robot_height = Column(Integer)
    programming_lang = Column(String(50))
    years_experience = Column(Integer)
    
    auto_scoring = Column(Boolean, default=False)
    auto_mobility = Column(Boolean, default=False)
    auto_paths = Column(Integer, default=0)
    
    can_climb = Column(Boolean, default=False)
    can_intake_ground = Column(Boolean, default=False)
    can_intake_source = Column(Boolean, default=False)
    can_shoot_speaker = Column(Boolean, default=False)
    can_score_amp = Column(Boolean, default=False)
    has_vision = Column(Boolean, default=False)
    
    strengths = Column(Text)
    weaknesses = Column(Text)
    strategy_notes = Column(Text)
    scouter_name = Column(String(100))
    
    robot_photo = Column(LargeBinary)
    photo_filename = Column(String(255))
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ScoutingSession", back_populates="pit_scouting")

class MatchScore(Base):
    """Match performance data for an FRC team."""
    __tablename__ = 'match_scores'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('scouting_sessions.id'), nullable=False)
    
    match_number = Column(Integer, nullable=False)
    frc_team = Column(String(20), nullable=False)
    alliance = Column(String(10))
    
    auto_leave = Column(Boolean, default=False)
    auto_high = Column(Integer, default=0)
    auto_low = Column(Integer, default=0)
    
    teleop_high = Column(Integer, default=0)
    teleop_low = Column(Integer, default=0)
    teleop_cycles = Column(Integer, default=0)
    
    endgame_status = Column(String(50))
    trap_scored = Column(Boolean, default=False)
    
    defense_rating = Column(Integer, default=3)
    driver_skill = Column(Integer, default=3)
    died_on_field = Column(Boolean, default=False)
    tipped_over = Column(Boolean, default=False)
    exploded = Column(Boolean, default =False)
    
    match_notes = Column(Text)
    scouter_name = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ScoutingSession", back_populates="match_scores")

class MatchSchedule(Base):
    """Match schedule for the competition."""
    __tablename__ = 'match_schedule'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('scouting_sessions.id'), nullable=False)
    
    match_number = Column(Integer, nullable=False)
    match_type = Column(String(20), default='Qualification')
    
    red_1 = Column(String(20))
    red_2 = Column(String(20))
    red_3 = Column(String(20))
    blue_1 = Column(String(20))
    blue_2 = Column(String(20))
    blue_3 = Column(String(20))
    
    scheduled_time = Column(DateTime)
    is_completed = Column(Boolean, default=False)

def get_engine():
    """Create database engine."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return create_engine(database_url, pool_pre_ping=True)

def get_session():
    """Create a new database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize the database tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
