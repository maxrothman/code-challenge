from contextlib import contextmanager
from enum import Enum
from functools import wraps

import sqlalchemy as db
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_FNAME = 'database.sqlite'

def get_engine():
    return db.create_engine(f'sqlite:///{DATABASE_FNAME}')

@contextmanager
def in_session():
    session = sessionmaker(bind=get_engine())()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def with_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with in_session() as s:
            return f(s, *args, **kwargs)
    return wrapper

def Column(*args, **kwargs):
    kwargs['nullable'] = kwargs.get('nullable', False)
    return db.Column(*args, **kwargs)

@as_declarative()
class Base:
    id = Column(db.Integer, primary_key=True)


class Question(Base):
    __tablename__ = 'questions'


class QuestionText(Base):
    __tablename__ = 'question_texts'

    text = Column(db.Text)
    version = Column(db.Integer)
    question_id = Column(db.Integer, db.ForeignKey('questions.id'))
    question = relationship('Question')

    __table_args__ = (db.UniqueConstraint('version', 'question_id'),)


class Answer(Base):
    __tablename__ = 'answers'

    text = Column(db.Text)
    question_text_id = Column(db.Integer, db.ForeignKey('question_texts.id'))
    user_id = Column(db.Integer, db.ForeignKey('users.id'))


# This set of categories is sticky, I'd want to be careful to match the categories to the ones used
# in the dataset being used to guide chatbot learning.
Sex = Enum('Sex', ['MALE', 'FEMALE', 'TRANS_MALE', 'TRANS_FEMALE', 'NOT_PROVIDED'])

class User(Base):
    __tablename__ = 'users'
    age = Column(db.Integer)
    sex = Column(db.Enum(Sex))


def _session_add(session, obj):
    session.add(obj)
    return obj


def get_latest_question_text(session, question_id):
    return (
        session.query(QuestionText)
        .filter(QuestionText.question_id == question_id)
        .order_by(db.desc(QuestionText.version))
        .limit(1)
    ).first()


def get_question_text_by_version(session, question_id, version):
    return (
        session.query(QuestionText)
        .filter(QuestionText.question_id == question_id)
        .filter(QuestionText.version == version)
    ).first()


def create_question(session, text):
    question = Question()
    question_text = QuestionText(text=text, version=0, question=question)
    session.add_all([
        question,
        question_text
    ])
    return question, question_text


def update_question_text(session, question_text_id, new_text):
    prev_qtext = session.query(QuestionText).get(question_text_id)
    return _session_add(session, QuestionText(
        text = new_text,
        version = prev_qtext.version + 1,
        question_id = prev_qtext.question_id,
    ))


def save_answer(session, question_text_id, user_id, answer):
    return _session_add(session, Answer(
        user_id = user_id,
        question_text_id = question_text_id,
        text = answer,
    ))


def create_user(session, sex, age):
    return _session_add(session, User(sex=sex, age=age))
