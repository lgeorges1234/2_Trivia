import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

from dotenv import load_dotenv
from pathlib import Path
import os

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

posgres_host = os.getenv("POSTGRES_HOST")
posgres_port = os.getenv("PORT_DEV")
database_name = os.getenv("POSTGRES_DB_DEV")
user_name = os.getenv("POSTGRES_USER_DEV")
user_password = os.getenv("POSTGRES_PASSWORD_DEV")


# database_path = 'postgresql://{}/{}'.format('localhost:5432', database_name)
database_path = f'postgresql://{user_name}:{user_password}@{posgres_host}:{posgres_port}/{database_name}'

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    # database_path = "postgresql://{}:{}@{}/{}".format(
    #     'trivia_user_test', 'password123_test', 'localhost:5432', 'trivia_test'
    # )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

"""
Question

"""
class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
            }

"""
Category

"""
class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
            }
