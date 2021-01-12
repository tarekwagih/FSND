import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
from pprint import pprint
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,  Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, DELETE, PATCH, OPTIONS')
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
      formated_categories = [category.format() for category in categories]
      
      return jsonify({ "categories" : formated_categories })
      

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  @cross_origin()
  def get_questions():
      page = request.args.get('page', 1, type=int)
      start = (page - 1 ) * 10
      end = start + 10
      questions = Question.query.all()
      formated_questions = [question.format() for question in questions]
      
      pprint(formated_questions)
      
      categories = Category.query.all()
      
      formated_categories = [category.format() for category in categories]
      pprint(formated_categories)

      current_category = Category.query.first()

      return jsonify({
        "questions": formated_questions[start:end],  
        "total_questions": len(questions),
        "categories": formated_categories,
        })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

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

      pprint(formated_questions)

      categories = Category.query.all()

      formated_categories = [category.format() for category in categories]
      pprint(formated_categories)

      current_category = Category.query.first()

      return jsonify({
          "questions": formated_questions[start:end],
          "total_questions": len(questions),
          "categories": formated_categories,
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
      print(category_id)
      questions = Question.query.all()
      formated_questions = [question.format() for question in questions]
      
      category_id = js_data['quiz_category']['id']
     # previous_question_id = js_data['previous_questions']['id']

      previous_question = Question.query.filter_by(category=category_id).one_or_none()
      formated_previous_question = [question.format() for question in questions]

      pprint(formated_questions)

      return jsonify({
          "showAnswer": False,
          "previousQuestions": formated_previous_question,
          "currentQuestion": formated_questions,
          "forceEnd": False
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
