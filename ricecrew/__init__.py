from flask import Flask
from ricecrew import settings

app = Flask(__name__)
app.config.from_object(settings)
