from flask import Flask, render_template, url_for, redirect, request, abort, Blueprint, jsonify, make_response
from static.data import db_session
from static.data.users import User
from static.data.jobs import Jobs
from datetime import datetime
from static.data.loginform import LoginForm
from static.data.registerform import RegisterForm
from static.data.registeruserform import RegisterUserForm
from requests import get
from static.data.editform import EditForm
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin
from static.data import user_api
import requests
from flask_restful import reqparse, abort, Api, Resource
from static.data import jobs_api
from PIL import Image
from static.data import users_resource
from static.data import jobs_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/works_log")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
@app.route('/works_log')
def works_log():
    config = {'title': 'Works log',
              'db_jobs': session.query(Jobs).all(),
              'db_users': session.query(User).all(),
              'd_list': []}
    for i in session.query(Jobs).all():
        try:
            config['d_list'].append(str(datetime.fromisoformat(i.end_date) - datetime.fromisoformat(i.start_date)))
        except:
            config['d_list'].append('Unknown')
    # print(datetime.fromisoformat(config['mdr'][0].end_date) - datetime.fromisoformat(config['mdr'][0].start_date))
    return render_template('works_log.html', **config)


@app.route('/register_job', methods=['GET', 'POST'])
def reqister_job():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs(
            team_leader=session.query(User).filter(User.name == form.teamlider.data.split()[0],
                                                   User.surname == form.teamlider.data.split()[1])[0].id,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            start_date=datetime(*list(map(int, form.start_date.data.split('.')))),
            end_date=datetime(*list(map(int, form.end_date.data.split('.')))),
            is_finished=form.is_finished.data
        )
        session.add(job)
        session.commit()
        return redirect('/works_log')
    return render_template('register_job.html', title='Регистрация работы', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.username.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/success')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/success')
def success():
    return render_template('success.html', title='Успешная регистрация')


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = EditForm()
    if request.method == "GET":
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          Jobs.user == current_user).first()
        if not jobs:
            jobs = session.query(Jobs).filter(Jobs.id == id,
                                              current_user.id == 1).first()
        if jobs:
            form.teamlider.data = jobs.team_leader
            form.job.data = jobs.job
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.start_date.data = jobs.start_date
            form.end_date.data = jobs.end_date
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          Jobs.user == current_user).first()
        if not jobs:
            jobs = session.query(Jobs).filter(Jobs.id == id,
                                              current_user.id == 1).first()
        if jobs:
            jobs.team_leader = form.teamlider.data
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.start_date = form.start_date.data
            jobs.end_date = form.end_date.data
            jobs.is_finished = form.is_finished.data
            session.commit()
            return redirect('/works_log')
        else:
            abort(404)
    return render_template('register_job.html', title='Редактирование новости', form=form)


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == id,
                                      Jobs.user == current_user).first()
    if not jobs:
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          current_user.id == 1).first()
    if jobs:
        session.delete(jobs)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/user_show/<int:user_id>')
def user_show(user_id):
    configure = {
        'title': 'Hometown',
        'data': get(f'http://localhost:8080/api/user/{user_id}').json()['user'],

    }
    toponym_to_find = configure["data"][0]["city_from"]

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        pass

    json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]

    to_size = toponym['boundedBy']['Envelope']
    delta_1 = float(to_size['upperCorner'].split()[0]) - float(to_size['lowerCorner'].split()[0])
    delta_2 = float(to_size['upperCorner'].split()[1]) - float(to_size['lowerCorner'].split()[1])
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    map_params = {
        "ll": ",".join([str(toponym_longitude), str(toponym_lattitude)]),
        "l": "sat",
        "spn": f'{delta_1},{delta_2}'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    configure['image_url'] = requests.get(map_api_server, params=map_params, stream=True).url
    return render_template('user_show.html', **configure)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    db_session.global_init("static/db/blogs.sqlite")
    session = db_session.create_session()
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint2)
    api.add_resource(users_resource.userListResource, '/api/v2/users')
    api.add_resource(users_resource.userResource, '/api/v2/users/<int:user_id>')
    api.add_resource(jobs_resource.jobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resource.jobsResource, '/api/v2/jobs/<int:jobs_id>')
    app.run(port=8080, host='127.0.0.1')

