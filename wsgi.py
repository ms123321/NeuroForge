"""Root WSGI module: gunicorn wsgi:app / waitress etc."""
from webapp.app import app as application

app = application
