from flask import Flask, render_template, url_for, redirect, request
from static.data import db_session
from static.data.users import User
from static.data.jobs import Jobs
from datetime import datetime
from static.data.loginform import LoginForm
from static.data.registerform import RegisterForm
from flask_login import LoginManager, login_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
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
@app.route('/index')
def index():
    return render_template('base.html', title='Главная')


@app.route('/works_log')
@login_required
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


@app.route('/success')
def success():
    return render_template('success.html', title='Успешная регистрация')


if __name__ == '__main__':
    db_session.global_init("static/db/blogs.sqlite")
    session = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
