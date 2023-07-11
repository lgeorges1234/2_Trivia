import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv
from pathlib import Path

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        # dotenv_path = Path('..env')
        # Specify the path of the .env file in the same directory
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path=dotenv_path)

        posgres_host = os.getenv("POSTGRES_HOST")
        posgres_port = os.getenv("PORT_DEV")
        database_name = os.getenv("POSTGRES_DB_TEST")
        user_name = os.getenv("POSTGRES_USER_TEST")
        user_password = os.getenv("POSTGRES_PASSWORD_TEST")


        self.app = create_app()
        self.client = self.app.test_client
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        # self.database_path = f'postgresql://{user_name}:{user_password}@{posgres_host}:{posgres_port}/{database_name}'
        # self.database_path = "postgresql://trivia_user_test:password123_test@127.0.0.1:5432/trivia_test"

        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "trivia_user_test", "password123_test", "localhost:5432", self.database_name
        )

        print(self.database_path)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get("/")
        data = json.loads(res.data)

        print(data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()