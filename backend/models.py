from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True)
    jobs = relationship('AudioJob', back_populates='user')

class AudioJob(Base):
    __tablename__ = 'audio_jobs'
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String, nullable=False)
    status = Column(String, default='processing')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    user = relationship('User', back_populates='jobs')
    transcript = relationship('Transcript', uselist=False, back_populates='job')
    questions = relationship('Question', back_populates='job')

class Transcript(Base):
    __tablename__ = 'transcripts'
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey('audio_jobs.id'))
    transcript_text = Column(Text)
    job = relationship('AudioJob', back_populates='transcript')

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey('audio_jobs.id'))
    question_text = Column(Text)
    answers = relationship('Answer', back_populates='question')
    job = relationship('AudioJob', back_populates='questions')

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_text = Column(Text)
    math_results = Column(JSON)
    question = relationship('Question', back_populates='answers')
