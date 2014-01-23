from datetime import datetime
from functools import wraps
from urlparse import urlparse
from flask import request, session, render_template, url_for, redirect
from ricecrew import app
from ricecrew.database import db_session
from ricecrew.generic_views import (View, DetailView, CreateView, UpdateView,
    DeleteView, view_class_decorator, classroute)
from ricecrew.models import BlogEntry, Event
from ricecrew.forms import LoginForm, BlogEntryForm
from ricecrew.utils import has_login, has_admin

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Authentication

def login_required(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        if not has_login():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return decorated_view


def admin_required(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        if not has_admin():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return decorated_view


def get_auth_redirect_url():
    next = request.values.get('next')
    if next:
        # Only redirect if the user-provided URL points back to this application
        netloc = urlparse(next)[1]
        if not netloc or netloc in app.config['ALLOWED_HOSTS']:
            return next
    return url_for('index')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm(formdata=request.form, csrf_context=session)
        if form.validate():
            session['user'] = form.username.data
            return redirect(get_auth_redirect_url())
    else:
        form = LoginForm(csrf_context=session)
    return render_template('login.html',
                           form=form, breadcrumbs=[('Log In', None)])


@app.route('/logout/')
@login_required
def logout():
    del session['user']
    return redirect(get_auth_redirect_url())


# Mixins

class BreadcrumbsMixin(object):
    def get_breadcrumbs(self):
        return getattr(self, 'breadcrumbs', [])

    def get_template_context(self):
        context = super(BreadcrumbsMixin, self).get_template_context()
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class BlogEntryMixin(object):
    model_class = BlogEntry
    form_class = BlogEntryForm
    redirect_view = 'entry_detail'

    def populate_obj(self):
        super(BlogEntryMixin, self).populate_obj()
        self.model.generate_markup()


# Concrete views

@app.route('/')
def index():
    entries = BlogEntry.query
    events = Event.query.filter(Event.start >= datetime.now())
    if not session.get('user'):
        entries = entries.filter(BlogEntry.public == True)
        events = events.filter(Event.public == True)

    last_entry = entries.order_by(BlogEntry.timestamp.desc()).first()
    upcoming_events = events.order_by(Event.start.asc())[:3]
    return render_template(
        'index.html', entry=last_entry, events=upcoming_events)


@app.route('/news/')
def blog():
    page_size = 10
    max_page = ((BlogEntry.query.count() - 1) / page_size) + 1

    try:
        page = int(request.args['page'])
    except KeyError, ValueError:
        page = 1
    else:
        page = max(1, min(page, max_page))

    start, end = (page - 1) * page_size, page * page_size
    entries = BlogEntry.query
    if not session.get('user'):
        entries = entries.filter(BlogEntry.public == True)
    entries = entries.order_by(BlogEntry.timestamp.desc())[start:end]

    return render_template('blog.html',
                           page=page, max_page=max_page, entries=entries,
                           breadcrumbs=[('News', url_for('blog'))])


@classroute('/news/<int:pk>/', 'entry_detail')
class EntryDetailView(BlogEntryMixin, BreadcrumbsMixin, DetailView):
    template = 'entry_detail.html'

    def get_breadcrumbs(self):
        return [
            ('News', url_for('blog')),
            (self.model.title, url_for('entry_detail', pk=self.kwargs['pk']))
        ]


@classroute('/news/add/', 'entry_create', methods=['GET', 'POST'])
@view_class_decorator(admin_required)
class EntryCreateView(BlogEntryMixin, BreadcrumbsMixin, CreateView):
    def get_breadcrumbs(self):
        return [
            ('News', url_for('blog')),
            ('Add BlogEntry', None)
        ]


@classroute('/news/<int:pk>/edit/', 'entry_update', methods=['GET', 'POST'])
@view_class_decorator(admin_required)
class EntryUpdateView(BlogEntryMixin, BreadcrumbsMixin, UpdateView):
    def get_breadcrumbs(self):
        return [
            ('News', url_for('blog')),
            (self.model.title, url_for('entry_detail', pk=self.kwargs['pk'])),
            ('Edit BlogEntry', None)
        ]


@classroute('/news/<int:pk>/delete/', 'entry_delete', methods=['GET', 'POST'])
@view_class_decorator(admin_required)
class EntryDeleteView(BreadcrumbsMixin, DeleteView):
    model_class = BlogEntry
    redirect_view = 'blog'

    def get_breadcrumbs(self):
        return [
            ('News', url_for('blog')),
            (self.model.title, url_for('entry_detail', pk=self.kwargs['pk'])),
            ('Delete BlogEntry', None)
        ]

    def get_redirect_context(self):
        return {}


# Static pages (about, etc.)

app.add_url_rule(
    '/about/', 'about', View.as_view(template='flatpages/about.html'))

app.add_url_rule(
    '/about/recruiting/', 'recruiting',
    View.as_view(template='flatpages/recruiting.html'))

app.add_url_rule(
    '/about/staff/', 'staff',
    View.as_view(template='flatpages/staff.html'))

app.add_url_rule(
    '/about/history/', 'history',
    View.as_view(template='flatpages/history.html'))
