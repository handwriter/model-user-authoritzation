from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField, IntegerField, DateTimeField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    teamlider = StringField('Team Lider (Name Surname)', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    start_date = StringField('Start Date (year/mounth/date/hour/minute/second)', validators=[DataRequired()])
    end_date = StringField('End Date (year/mounth/date/hour/minute/second)', validators=[DataRequired()])
    is_finished = BooleanField('Is finished', validators=[DataRequired()])
    submit = SubmitField('Войти')