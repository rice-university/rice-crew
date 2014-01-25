from flask import Flask, Response
from ricecrew import settings

class XhtmlResponse(Response):
    default_mimetype = 'application/xhtml+xml'

app = Flask(__name__)
app.config.from_object(settings)
app.response_class = XhtmlResponse
