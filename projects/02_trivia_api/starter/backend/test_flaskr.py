import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('postgres:tarek@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_question = {
            'question': 'Test Creation ?',
            'answer': 'True',
            'category': 1,
            'difficulty': 5
        }
        
        self.search = {
            'searchTerm' : 'test'
        }
        
        self.queizzes = {
            'previous_questions': [], 
            'quiz_category': {'id': 0, 'type': 'click'}
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        """Test categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        """Test questions """
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        """Test delete question """
        res = self.client().delete('/questions/73')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 73).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_404_if_not_exist_delete_question(self):
        """Test 404 if not exist question """
        res = self.client().delete('/questions/34')
        self.assertEqual(res.status_code, 404)

    def test_create_question(self):
        """Test create question """
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        """Test search question """
        res = self.client().post('/search', json=self.search)
        data = json.loads(res.data)
        search_term = self.search['searchTerm']
        search_like = "%{}%".format(search_term)
        questions = Question.query.filter(Question.question.ilike(search_like)).count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], questions)

    def test_get_questions_by_category(self):
        """Test get question by category """
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.category == 1).count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], questions)

    def test_500_error_get_questions_by_category(self):
        """Test get question by category """
        res = self.client().get('/categories/1000/questions')
        self.assertEqual(res.status_code, 500)


    def test_quizzes(self):
        """Test quizzes """
        res = self.client().post('/quizzes', json=self.queizzes)
        data = json.loads(res.data)
        category = self.queizzes['quiz_category']['id']
        questions = Question.query.filter(Question.category == category).count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404(self):
        """Test 404 """
        res = self.client().get('/not_found')
        self.assertEqual(res.status_code, 404)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
