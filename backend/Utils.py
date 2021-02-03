import random

from flask import abort, jsonify
from sqlalchemy.orm import load_only
from sqlalchemy.sql import func

from models import Category, Question, db


def get_paginatied_data(model_data, current_page, window_size):
    last_index = min(len(model_data), (current_page + 1) * window_size)
    start_index = current_page * window_size
    print("current_page = {} start_index = {} and end_index = {}".format(current_page,start_index, last_index))
    window_data = model_data[start_index: last_index]
    return [question.format() for question in window_data]


def get_questions_main(page, questions, window_size, current_category=None):
    total_available_page = len(questions) / window_size
    print("total_avavilable_page = {}".format(total_available_page))
    if page > total_available_page and len(questions) % window_size == 0:
        # for page data is not available in the database returning 404
        abort(404)
    page_questions = get_paginatied_data(questions, page, window_size)
    print("{}".format(page_questions))
    categories = Category.query.all()
    if categories is None:
        abort(422)
    categories = {k.id: k.type for k in (categories)}
    return jsonify({
        "total_questions": len(questions),
        "questions": page_questions,
        "categories": categories,
        "current_category": current_category}), 200


def load_only_random(model):
    return random.choice(model.query.options(load_only('id')).all())


def optimized_question_random():
    return Question.query.filter.options(load_only('id')).offset(
        func.floor(
            func.random() *
            db.session.query(func.count(Question.id))
        )
    ).limit(1).all()
