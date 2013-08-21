from wtforms import Form, TextField, TextAreaField, DateTimeField, BooleanField
from wtforms.ext.csrf.session import SessionSecureForm
from ricecrew import app


class SecureForm(SessionSecureForm):
    SECRET_KEY = app.config['SECRET_KEY']


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
