"""Formularios WTForms para la app."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Formulario de login admin."""

    username = StringField(
        "Usuario",
        validators=[DataRequired(message="El usuario es requerido")],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es requerida")],
    )
