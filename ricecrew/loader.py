# Imports the app object and everything needed to make the site work. (This
# isn't done in __init__.py to avoid circular imports.) When deploying the site,
# point your WSGI server to this module.

from ricecrew import app, views
