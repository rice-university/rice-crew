from datetime import datetime
from flask import request, session, render_template, url_for, redirect
from ricecrew import app
from ricecrew.database import db_session
from ricecrew.models import BlogEntry, Event
from ricecrew.forms import SecureForm, BlogEntryForm

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# A version of Flask's app.route decorator for class-based views
def classroute(rule, endpoint, **options):
    def decorator(cls):
        app.add_url_rule(rule, endpoint, cls.as_view(), **options)
        return cls
    return decorator


# Base view classes

class View(object):
    '''
    Base view which renders a template. Subclasses should provide the attribute
    'template'.
    '''

    def dispatch(self, *args, **kwargs):
        if request.method == 'POST':
            return self.post(*args, **kwargs)
        else:
            return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.render()

    def render(self):
        return render_template(self.template, **self.get_template_context())

    def get_template_context(self):
        return {}

    @classmethod
    def as_view(cls):
        def view(*args, **kwargs):
            self = cls()
            return self.dispatch(*args, **kwargs)
        return view


class FormView(View):
    '''
    View for handling forms. Subclasses should provide the attributes
    'form_class', 'redirect_view', and 'template'.
    '''

    def get(self, *args, **kwargs):
        self.form = self.form_class(csrf_context=session, **self.get_form_context())
        return self.render()

    def post(self, *args, **kwargs):
        self.form = self.form_class(formdata=request.form, csrf_context=session)
        if self.form.validate():
            return self.form_valid()
        return self.render()

    def form_valid(self):
        return redirect(url_for(self.redirect_view,
                                **self.get_redirect_context()))

    def get_form_context(self):
        return {}

    def get_redirect_context(self):
        return {}

    def get_template_context(self):
        context = super(FormView, self).get_template_context()
        context['form'] = self.form
        return context


class ModelFetchMixin(object):
    '''
    View mixin for retreiving a model instance via primary key. Subclasses
    should provide the attribute 'model_class'.
    '''

    def dispatch(self, pk, *args, **kwargs):
        self.model = self.model_class.query.get(pk)
        if self.model is None:
            abort(404)
        return super(ModelFetchMixin, self).dispatch(*args, **kwargs)

    def get_template_context(self):
        context = super(ModelFetchMixin, self).get_template_context()
        context['model'] = self.model
        return context


class ModelEditMixin(object):
    '''
    View mixin for editing a model instance.
    '''

    def form_valid(self):
        self.populate_obj()
        db_session.commit()
        return super(ModelEditMixin, self).form_valid()

    def populate_obj(self):
        self.form.populate_obj(self.model)

    def get_redirect_context(self):
        context = super(ModelEditMixin, self).get_redirect_context()
        context['pk'] = self.model.id
        return context


class DetailView(ModelFetchMixin, View):
    pass


class CreateView(ModelEditMixin, FormView):
    template = 'add_edit.html'

    def form_valid(self):
        self.model = self.model_class()
        db_session.add(self.model)
        return super(CreateView, self).form_valid()


class UpdateView(ModelFetchMixin, ModelEditMixin, FormView):
    template = 'add_edit.html'

    def get_form_context(self):
        context = super(UpdateView, self).get_form_context()
        context['obj'] = self.model
        return context


class DeleteView(ModelFetchMixin, FormView):
    form_class = SecureForm
    template = 'delete.html'

    def form_valid(self):
        db_session.delete(self.model)
        db_session.commit()
        return super(DeleteView, self).form_valid()


# Model mixins

class BlogEntryMixin(object):
    model_class = BlogEntry
    form_class = BlogEntryForm
    redirect_view = 'blog'

    def populate_obj(self):
        super(BlogEntryMixin, self).populate_obj()
        self.model.generate_markup()

    def get_redirect_context(self):
        return {}


# Concrete views

@app.route('/')
def index():
    last_entry = BlogEntry.query.order_by(BlogEntry.date_posted.desc()).first()
    events = Event.query.filter(
        Event.start_date >= datetime.now()
    ).order_by(Event.start_date.asc())[:3]

    return render_template('index.html', entry=last_entry, events=events)


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
    entries = BlogEntry.query.order_by(BlogEntry.date_posted.desc())[start:end]

    return render_template(
        'blog.html', page=page, max_page=max_page, entries=entries)


@classroute('/news/<int:pk>/', 'entry_detail')
class EntryDetailView(BlogEntryMixin, DetailView):
    template = 'entry_detail.html'


@classroute('/news/add/', 'entry_create', methods=['GET', 'POST'])
class EntryCreateView(BlogEntryMixin, CreateView):
    pass


@classroute('/news/<int:pk>/edit/', 'entry_update', methods=['GET', 'POST'])
class EntryUpdateView(BlogEntryMixin, UpdateView):
    pass


@classroute('/news/<int:pk>/delete/', 'entry_delete', methods=['GET', 'POST'])
class EntryDeleteView(BlogEntryMixin, DeleteView):
    pass

