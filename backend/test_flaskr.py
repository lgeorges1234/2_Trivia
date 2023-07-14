import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv
from pathlib import Path


# dotenv_path = Path('..env')
# Specify the path of the .env file in the same directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

posgres_host = os.getenv("POSTGRES_HOST")
posgres_port = os.getenv("PORT_DEV")
database_name = os.getenv("POSTGRES_DB_TEST")
user_name = os.getenv("POSTGRES_USER_TEST")
user_password = os.getenv("POSTGRES_PASSWORD_TEST")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_path = f'postgresql://{user_name}:{user_password}@{posgres_host}:{posgres_port}/{database_name}'

        test_config = {
            'DATABASE_URI': self.database_path
        }

        self.app = create_app(test_config['DATABASE_URI'])
        self.client = self.app.test_client

        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Heres a new question string",
            "answer": "Heres a new answer string",
            "difficulty": 1,
            "category": 3
            }
        
        self.new_quizzes = {
            "quiz_category":2,
            "previous_questions":[16,18,19]
        }

        self.new_quizzes = {
            'previous_questions': [16,18,19],
            'quiz_category': {
                'type': 'Art',
                'id': 2
            }}

        
        self.bad_formated_question = {"remark": "this is not what expected"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "Which"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 7)

    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "bulibulabululi"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.bad_formated_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_question_delete(self):
        res_id = self.client().post("/questions", json={"searchTerm": "Heres a new question string"})
        data_id = json.loads(res_id.data)
        question_id = data_id["questions"][0]["id"]
        self.client().delete("/questions/" + str(question_id))
        res = self.client().post("/questions", json={"searchTerm": "Heres a new question string"})
        data_id = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data_id["questions"]), 0)

    def test_422_if_question_delete_fails(self):
        res = self.client().delete("/questions/1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"], 4)

    def test_422_if_question_by_category_fails(self):
        res = self.client().get('/categories/50/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_quizzes(self):
        res = self.client().post("/quizzes", json=self.new_quizzes)
        data = json.loads(res.data)

        print(data['question']['id'])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"]["id"], 17)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()