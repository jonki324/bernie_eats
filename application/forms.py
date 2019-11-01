from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    login_id = StringField('ログインID',
                           validators=[DataRequired('必須です'),
                                       Length(max=20, message='20桁までです')])
    password = PasswordField('パスワード',
                             validators=[DataRequired('必須です'),
                                         Length(max=20, message='20桁までです')])
