from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddPollForm(FlaskForm):
    description = StringField('Poll text', validators=[DataRequired()])
    submit = SubmitField('Submit')
