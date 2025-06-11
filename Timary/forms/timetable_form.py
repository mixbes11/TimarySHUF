from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class TimetableForm(FlaskForm):
    lesson = StringField('Урок', validators=[DataRequired()], render_kw={"placeholder": "  Урок"})
    room = StringField('Кабинет', validators=[DataRequired()], render_kw={"placeholder": "  Кабинет"})
    date = DateField('Дата', format='%d.%m.%Y', validators=[DataRequired()])
    hour = IntegerField('Часы', validators=[DataRequired(), NumberRange(min=0, max=23)], render_kw={"placeholder": "ЧЧ"})
    minute = IntegerField('Минуты', validators=[DataRequired(), NumberRange(min=0, max=59)], render_kw={"placeholder": "ММ"})
    submit = SubmitField('Добавить/Изменить')