from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import Length


class OrderForm(FlaskForm):
    order_count_buta = StringField('注文数',
                                   validators=[Length(max=99, message='99までです')])
    order_count_modern = StringField('注文数',
                                     validators=[Length(max=99, message='99までです')])
