from flask import Flask, render_template, url_for, redirect, request
from static.data import db_session
from static.data.users import User
from static.data.jobs import Jobs
from datetime import datetime
from static.data.loginform import LoginForm
from flask_login import LoginManager, login_user

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
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Главная')
if __name__ == '__main__':
    db_session.global_init("static/db/blogs.sqlite")
    session = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
