import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


#---------------------------------------
#           Utility functions
#---------------------------------------

def paginate(request, selection):
    page = request.args.get("page",1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def get_categories(category_id=None):
    categories_dict = {}
    if category_id:
        categories_dict = Category.query.get(category_id)
    else:
        categories_dict = {categorie.id: categorie.type for categorie in Category.query.distinct().all()}
    
    return categories_dict


#---------------------------------------
#           Flask App
#---------------------------------------

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    if test_config:
        setup_db(app, test_config)
    else:
        setup_db(app)


    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    """
    set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    @app.route('/')
    def check_server():
     return "server running"

    """
    Endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = get_categories()
        return jsonify({'categories': categories})

    """
    Endpoint to handle GET requests for questions, including pagination (every 10 questions).
    This endpoint should return a list of questions, number of total questions, current category, categories.
    """
    
    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": get_categories(),
                "currentCategory": None,
            }
        )

    """
    Endpoint to DELETE question using a question ID.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def search_by_category(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            return jsonify(
              {
                  "success": True,
                  "deleted": question_id,
                  "total_questions": len(Question.query.all()),
                  "currentCategory": None
              }
            ), 200

        except:
            abort(422)

    """
    Endpoint to POST a new question, which will require the question and answer text,
    category, and difficulty score.The endpoint also allows to get questions based on a search term.
    It returns any questions for whom the search term is a substring of the question.
    """

    @app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()
        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        search = body.get("searchTerm", None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                ).all()
            elif question and answer and difficulty and category:
                question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
            else:
                abort(422)

            current_questions = paginate(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "categories": get_categories(),
                    "currentCategory": None,
                }
            )

        except:
            abort(422)

    """
    Endpoint to GET questions based on category.
    """

    @app.route('/categories/<int:category_id>/questions')
    def get_question_categories(category_id):
        try:
            selection = Question.query.filter(Question.category==category_id).all()
            current_questions = paginate(request, selection)

            category = get_categories(category_id).format()

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "currentCategory": category,
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=['POST'])
    def play_game():
        body = request.get_json()
        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category", None).get("id")

        try:
            if quiz_category:
                questions = Question.query.filter(Question.category == quiz_category).all()
            else:
                questions = Question.query.all()

            question = None

            while len(previous_questions) < len(questions):
                question = random.choice([q for q in questions if q not in previous_questions])
                if question.id not in previous_questions:
                    break
    
            return jsonify(
                    {
                        "question": question.format()
                    }
                ),200

        except:
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )



    return app
    # if __name__ == '__main__':
    #     app.run()

# $env:FLASK_APP='flaskr'
# $env:FLASK_ENV='development'
# python -m flask run