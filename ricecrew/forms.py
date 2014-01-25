from functools import wraps
from cgi import escape
from wtforms import (Form, TextField, TextAreaField, DateTimeField,
                     BooleanField, PasswordField, HiddenField,
                     widgets, validators)
from wtforms.ext.csrf.session import SessionSecureForm
from ricecrew import app


# WTFORMS XHTML FIX

# This is a terrible hack, but as of this writing there's no way to
# to make wtforms output valid XHTML, so we monkey-patch the correct
# behavior in.

def xhtml_params(**kwargs):
    params = []
    for k,v in sorted(kwargs.iteritems()):
        if k in ('class_', 'class__', 'for_'):
            k = k[:-1]
        if v is True:
            params.append('%s="%s"' % (unicode(k), unicode(k)))
        else:
            params.append(
                '%s="%s"' % (unicode(k), escape(unicode(v), quote=True)))
    return ' '.join(params)

def patch_widget(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        return widgets.HTMLString(func(*args, **kwargs)[:-1] + '/>')
    return decorator

widgets.html_params.__code__ = xhtml_params.__code__
widgets.Input.html_params = staticmethod(xhtml_params)
widgets.Input.__call__ = patch_widget(widgets.Input.__call__)
widgets.FileInput.__call__ = patch_widget(widgets.FileInput.__call__)


# Form classes

class SecureForm(SessionSecureForm):
    SECRET_KEY = app.config['SECRET_KEY']


class LoginForm(SecureForm):
    username = TextField(validators=[validators.InputRequired()])
    password = PasswordField(validators=[validators.InputRequired()])

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
    title = TextField(validators=[validators.InputRequired()])
    body = TextAreaField(validators=[validators.InputRequired()],
                         description='The body of the entry in Markdown format '
                         '(see http://daringfireball.net/projects/markdown/)')
    public = BooleanField()


class EventForm(SecureForm):
    start_date = DateTimeField()
    end_date = DateTimeField()
    title = TextField()
    description = TextAreaField()
    public = BooleanField()
