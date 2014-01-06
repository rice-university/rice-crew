from functools import wraps
from flask import request, session, render_template, url_for, redirect, abort
from ricecrew import app
from ricecrew.database import db_session
from ricecrew.forms import SecureForm


# Base view classes

class View(object):
    '''
    Base view which renders a template. Subclasses should provide the attribute
    'template'.
    '''

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def dispatch(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        if request.method == 'POST':
            return self.post()
        else:
            return self.get()

    def get(self):
        return self.render()

    def render(self):
        return render_template(self.template, **self.get_template_context())

    def get_template_context(self):
        return {}

    @classmethod
    def as_view(cls, *init_args, **init_kwargs):
        def view(*args, **kwargs):
            self = cls(*init_args, **init_kwargs)
            return self.dispatch(*args, **kwargs)
        return view


class FormView(View):
    '''
    View for handling forms. Subclasses should provide the attributes
    'form_class', 'redirect_view', and 'template'.
    '''

    def get(self):
        self.form = self.form_class(
            csrf_context=session, **self.get_form_context())
        return self.render()

    def post(self):
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


# Mixins

class ModelFetchMixin(object):
    '''
    View mixin for retreiving a model instance via primary key. Subclasses
    should provide the attribute 'model_class'.
    '''

    def dispatch(self, pk, *args, **kwargs):
        self.model = self.model_class.query.get(pk)
        if self.model is None:
            abort(404)
        elif hasattr(self.model, 'public') and not (
                self.model.public or session.get('user')):
            return redirect(url_for('login', next=request.path))
        return super(ModelFetchMixin, self).dispatch(pk=pk, *args, **kwargs)

    def get_template_context(self):
        context = super(ModelFetchMixin, self).get_template_context()
        context['model'] = self.model
        return context


class ModelEditMixin(object):
    '''
    View mixin for editing a model instance. Subclasses should provide the
    attribute 'model' when receiving a POST request containing valid form data.
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


# Composed view classes

class DetailView(ModelFetchMixin, View):
    pass


class CreateView(ModelEditMixin, FormView):
    template = 'create.html'

    def form_valid(self):
        self.model = self.model_class()
        db_session.add(self.model)
        return super(CreateView, self).form_valid()

    def get_template_context(self):
        context = super(CreateView, self).get_template_context()
        context['model_name'] = self.model_class.__name__
        return context


class UpdateView(ModelFetchMixin, ModelEditMixin, FormView):
    template = 'update.html'

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


# Decorators

def view_class_decorator(func_decorator):
    '''
    Adapts view function decorators to class-based views
    '''

    def decorator(cls):
        as_view = cls.as_view
        @wraps(as_view)
        def as_decorated_view(cls, *args, **kwargs):
            return func_decorator(as_view(*args, **kwargs))
        cls.as_view = classmethod(as_decorated_view)
        return cls
    return decorator


def classroute(rule, endpoint, **options):
    '''
    A version of Flask's app.route decorator for class-based views
    '''

    def decorator(cls):
        app.add_url_rule(rule, endpoint, cls.as_view(), **options)
        return cls
    return decorator
