from wtforms import (Form, TextField, TextAreaField, DateTimeField,
                     BooleanField, PasswordField)
from wtforms.ext.csrf.session import SessionSecureForm
from ricecrew import app


class SecureForm(SessionSecureForm):
    SECRET_KEY = app.config['SECRET_KEY']


class LoginForm(SecureForm):
    username = TextField()
    password = PasswordField()

    def validate(self):
        result = super(LoginForm, self).validate()
        if result:
            user = app.config['USERS'].get(self.username.data)
            if user is None or self.password.data != user[1]:
                self.password.errors.append(
                    self.password.gettext('Invalid credentials.'))
                return False
        return result


class BlogEntryForm(SecureForm):
    title = TextField()
    body = TextAreaField()
    public = BooleanField()


class EventForm(SecureForm):
    start_date = DateTimeField()
    end_date = DateTimeField()
    title = TextField()
    description = TextAreaField()
    public = BooleanField()
