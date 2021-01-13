import os
from flask import Flask, request, abort, jsonify
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
from pprint import pprint
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,  Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, DELETE, PATCH, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    @cross_origin()
    def get_categories():
        categories = Category.query.all()
        formated = {}
        for category in categories:
            formated[category.id] = category.type

        return jsonify({
            "success": True,
            "categories": formated
            })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of
    the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    @cross_origin()
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formated_questions = [question.format() for question in questions]

        categories = Category.query.all()

        formated_categories = {}
        for category in categories:
            formated_categories[category.id] = category.type

        return jsonify({
            "success": True,
            "questions": formated_questions[start:end],
            "total_questions": len(questions),
            "categories": formated_categories,
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    @cross_origin()
    def delete_questions(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question:
            question.delete()
            return jsonify({"success": True})
        else:
            abort(404)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at
    the end of the last page of the questions
    list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def add_questions():
        js_data = json.loads(request.data)
        question = js_data['question']
        answer = js_data['answer']
        difficulty = js_data['difficulty']
        category = js_data['category']
        qu = Question(
            question=question,
            answer=answer,
            difficulty=difficulty,
            category=category
        )
        qu.insert()
        if question:
            return jsonify({"success": True})
        else:
            abort(400)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/search', methods=['POST'])
    @cross_origin()
    def search_questions():
        js_data = json.loads(request.data)
        search_term = js_data['searchTerm']
        search_like = "%{}%".format(search_term)
        questions = Question.query.\
            filter(Question.question.ilike(search_like)).all()
        formated_questions = [question.format() for question in questions]

        if questions:
            questions_category = Question.query.\
                filter(Question.question.ilike(search_like)).first()
            current_category = Category.query.\
                filter(Category.id == questions_category.category).first()
            formated_category = current_category.format()
        else:
            formated_category = []

        return jsonify({
            "success": True,
            "questions": formated_questions,
            "total_questions": len(questions),
            "current_category": formated_category

        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    @cross_origin()
    def get_questions_by_category(cat_id):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.filter(Question.category == cat_id).all()
        formated_questions = [question.format() for question in questions]

        categories = Category.query.all()
        formated_categories = [category.format() for category in categories]

        current_category = Category.query.first()
        current_category_f = current_category.format()

        return jsonify({
            "success": True,
            "questions": formated_questions[start:end],
            "total_questions": len(questions),
            "categories": formated_categories,
            "current_category": current_category_f
        })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    @cross_origin()
    def get_questions_for_quizz():
        js_data = json.loads(request.data)
        pprint(js_data)
        category_id = js_data['quiz_category']['id']

        previous_question_id = js_data['previous_questions']

        if previous_question_id:
            previous_question = Question.query.\
                filter(Question.id == previous_question_id[0]).first()
            formated_previous_question = previous_question.format()
            if category_id != 0:
                condetion = Question.category == category_id
                condetion_2 = Question.id != previous_question.id
                if Question.query.filter(condetion, condetion_2).count() != 0:
                    query = Question.query.filter(condetion, condetion_2)
                    q_question = query.all()
                    question = random.choice(q_question)
                else:
                    question = {}
            else:
                condetion_else = Question.id != previous_question.id
                query_else = Question.query.filter(condetion_else).all()
                question = random.choice(query_else)
            if question:
                formated_question = question.format()
            else:
                formated_question = False

        else:
            formated_previous_question = {}
            if category_id != 0:
                cond_prev = Question.category == category_id
                if Question.query.filter(cond_prev).count() != 0:
                    query_prev = Question.query.filter(cond_prev).all()
                    question = random.choice(query_prev)
                else:
                    question = {}
            else:
                question = random.choice(Question.query.all())
            if question:
                formated_question = question.format()
            else:
                formated_question = False

        return jsonify({
            "success": True,
            "question": formated_question
        })

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422

    @app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "unprocessable"
            }), 400

    @app.errorhandler(405)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app

app = create_app()

# Default port:
if __name__ == '__main__':
    app.run()
