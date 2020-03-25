from flask import Flask, render_template, url_for, redirect, request, abort, Blueprint, jsonify, make_response
from . import db_session
from .jobs import Jobs
from .users import User
from requests import get


blueprint2 = Blueprint('user_api', __name__,
                      template_folder='templates')


@blueprint2.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    session = db_session.create_session()
    users = session.query(User).filter(User.id == user_id)
    return jsonify(
        {
            'user':
                [item.to_dict()
                 for item in users]
        }
    )


@blueprint2.route('/api/user')
def get_user():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict()
                 for item in users]
        }
    )


@blueprint2.route('/api/user', methods=['POST'])
def create_user():
    session = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 session.execute('SELECT * FROM users').keys()) or 'password' not in request.json.keys():
        return jsonify({'error': 'Bad request'})
    user = User()
    user.set_password(request.json['password'])
    for i in session.execute('SELECT * FROM users').keys():
        if i == 'hashed_password' or i == 'modified_date':
            continue
        user.__setattr__(i, request.json[i])
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        if 'UNIQUE' in str(e):
            return jsonify({'error': 'Id already exists'})
        elif 'unsupported type' in str(e):
            return jsonify({'error': 'One of args has unsupported type'})
        else:
            return jsonify({'error': str(e).split('\n')[0]})
    return jsonify({'success': 'OK'})


@blueprint2.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint2.route('/api/user/<int:user_id>', methods=['PUT'])
def change_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    if len(set(session.execute('SELECT * FROM users').keys()).intersection(set(request.json.keys()))) != len(
            request.json.keys()):
        return jsonify({'error': 'Incorrect attributes'})
    for i in request.json.keys():
        if type(user.__getattribute__(i)) != type(request.json[i]):
            return jsonify({'error': 'Incorrect type of any args'})
        user.__setattr__(i, request.json[i])
    session.commit()
    return jsonify({'success': 'OK'})