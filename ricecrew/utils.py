from pytz import utc
from flask import session
from ricecrew import app

@app.template_global()
def has_login():
    user = session.get('user')
    if user is not None:
        if user in app.config['USERS']:
            return True
        else:
            del session['user']
    return False

@app.template_global()
def has_admin():
    return has_login() and app.config['USERS'][session['user']][0]

@app.template_global()
def localtime(naive_dt):
    return utc.localize(naive_dt).astimezone(app.config['TIMEZONE'])
