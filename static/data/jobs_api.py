from flask import Flask, render_template, url_for, redirect, request, abort, Blueprint, jsonify, make_response
from . import db_session
from .jobs import Jobs
from .users import User
from requests import get


blueprint = Blueprint('jobs_api', __name__,
                      template_folder='templates')


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_jobs_by_id(job_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == job_id)
    return jsonify(
        {
            'jobs':
                [item.to_dict()
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict()
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished', 'id']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    jobs = Jobs(
        id=request.json['id'],
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        start_date=request.json['start_date'],
        end_date=request.json['end_date'],
        is_finished=request.json['is_finished'],
        user=User(name='Anonimous')
    )
    session.add(jobs)
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


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['DELETE'])
def delete_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    session.delete(jobs)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['PUT'])
def change_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    if len(set(session.execute('SELECT * FROM jobs').keys()).intersection(set(request.json.keys()))) != len(
            request.json.keys()):
        return jsonify({'error': 'Incorrect attributes'})
    for i in request.json.keys():
        if type(jobs.__getattribute__(i)) != type(request.json[i]):
            return jsonify({'error': 'Incorrect type of any args'})
        jobs.__setattr__(i, request.json[i])
    session.commit()
    return jsonify({'success': 'OK'})