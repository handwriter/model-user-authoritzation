from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, url_for, redirect, request, abort, Blueprint, jsonify, make_response
from . import db_session
from .jobs import Jobs
from .users import User


parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True, type=int)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('start_date', required=True)
parser.add_argument('end_date', required=True)
parser.add_argument('is_finished', required=True, type=bool)


class jobsResource(Resource):
    def get(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        return jsonify({'jobs': jobs.to_dict()})

    def delete(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        session.delete(jobs)
        try:
            session.commit()
        except Exception as e:
            return jsonify({'error': str(e)})
        return jsonify({'success': 'OK'})


class jobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict() for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        jobs = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            start_date=args['start_date'],
            end_date=args['end_date'],
            is_finished=args['is_finished']
        )
        jobs.user = User(name='Anonimous')
        session.add(jobs)
        try:
            session.commit()
        except Exception as e:
            if 'UNIQUE' in str(e):
                return jsonify({'error': 'One of unique args in not unique'})
            else:
                return jsonify({'error': str(e)})
        return jsonify({'success': 'OK'})


def abort_if_jobs_not_found(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        abort(404)