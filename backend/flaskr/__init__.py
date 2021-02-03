import random

from Utils import get_questions_main
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db, Category, Question, db
from sqlalchemy import and_

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route("/categories", methods=["GET"])
    def categories():
        categories = Category.query.all()
        if categories is None:
            abort(422)
        categories = {k.id: k.type for k in (categories)}
        return jsonify({"categories":categories})

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

    @app.route("/questions", methods=["GET"])
    def get_questions():
        print(request.args.keys())
        page = get_page_number()
        questions = Question.query.all()
        return get_questions_main(page, questions, QUESTIONS_PER_PAGE)

    def get_page_number():
        page = int(request.args.get("page", 0))
        print("page = {}".format(page))
        if page > 0:
            page = page - 1
        return page

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_questions(question_id):

        print("question_id = {}".format(question_id))
        question = Question.query.get(question_id)
        print(question)
        if question is None:
            print("inside abort")
            abort(404)
        try:
            question.delete()
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Question Deleted Successfully"
            })
        except Exception as e:
            abort(400)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route("/questions", methods=["POST"])
    def create_question():
        request_data = request.get_json()
        print(request_data)
        question = Question(request_data["question"], request_data["answer"], request_data["category"],
                            int(request_data["difficulty"]))
        print(question.format())
        question.insert()
        return jsonify({
            "success": True,
            "message": "success"
        }), 200
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route("/questions/search/", methods=["POST"])
    def search_question():
        data = request.get_json()
        print(data)
        search_key = data["searchTerm"].lower()
        print(search_key)
        question = db.session.query(Question).filter(Question.question.ilike("%{}%".format(search_key))).all()
        print(question.__str__())
        return get_questions_main(0, question, QUESTIONS_PER_PAGE)
    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def search_based_on_category(category_id):
        page = get_page_number()
        question = db.session.query(Question).filter(Question.category == category_id).all()
        return get_questions_main(page, question, QUESTIONS_PER_PAGE, category_id)
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

    @app.route("/quizzes", methods=["POST"])
    def show_quizzes():
        data = request.get_json()
        print(data)
        previous_questions = list(data["previous_questions"])
        category_id = int(data["quiz_category"]['id'])
        if category_id > 0:
            questions = db.session.query(Question).filter(and_(
                Question.category == category_id,  Question.id.notin_(previous_questions))).all()
        else:
            questions = db.session.query(Question).filter(Question.id.notin_(previous_questions)).all()

        questions = [question.format() for question in questions]
        if len(questions) > 0:
            return jsonify({"question": random.choice(questions)})
        return jsonify({
            "success": True
        }), 200
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
            "message": "Resource Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unable to process request"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Bad Request received"
        }), 500

    @app.errorhandler(405)
    def method_error(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Request method is not supported"
        }), 405

    return app
