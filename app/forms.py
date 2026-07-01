from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Admin login form with CSRF protection."""

    username = StringField(
        'Usuario',
        validators=[DataRequired(message='El usuario es requerido')],
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='La contraseña es requerida')],
    )
    submit = SubmitField('Iniciar sesión')
