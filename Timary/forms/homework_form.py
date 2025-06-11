from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, HiddenField
from wtforms.validators import DataRequired


class HomeworkForm(FlaskForm):
    task = StringField('Задание', validators=[DataRequired()], render_kw={"placeholder": "Задание"})
    lesson = StringField('Урок', validators=[DataRequired()], render_kw={"placeholder": "Урок"})
    date = DateField('Дата', format='%d.%m.%Y', validators=[DataRequired()])
    ready = StringField('Готовность', validators=[DataRequired()], render_kw={"placeholder": "Готовность"})
    file = HiddenField(default='nothing')
    submit = SubmitField('Добавить/Изменить')
