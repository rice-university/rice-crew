from datetime import datetime
from HTMLParser import HTMLParser
from sqlalchemy import Column, Integer, String, DateTime, Boolean
import markdown
from ricecrew.database import Base


class PreviewParser(HTMLParser):
    '''
    HTMLParser subclass for generating blog post previews. The get_preview()
    method will generate a "preview" of a given piece of HTML which contains
    at most the specified number of characters and images.
    '''

    def __init__(self, length, images):
        HTMLParser.__init__(self)
        self.length = length
        self.images = images

    def build_element(self, tag, attrs, close=False):
        fstr = '<{} {} />' if close else '<{} {}>'
        return fstr.format(tag, ' '.join('{}="{}"'.format(*x) for x in attrs))

    def handle_start_or_startend(self, tag, attrs, startend=False):
        if tag == 'img':
            if self.images > 0:
                self.parts.append(self.build_element(tag, attrs, startend))
                self.images -= 1
                self.tag_stack.append(tag)
            else:
                self.truncated = True
        elif self.length > 0:
            self.parts.append(self.build_element(tag, attrs, startend))
            self.tag_stack.append(tag)
        else:
            self.truncated  = True

    def handle_starttag(self, tag, attrs):
        self.handle_start_or_startend(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.handle_start_or_startend(tag, attrs, True)

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
            self.parts.append('</{}>'.format(tag))

    def handle_data(self, data):
        if self.length > 0:
            if len(data) > self.length:
                self.truncated = True
                while not data[self.length - 1].isspace() and self.length > 1:
                    self.length -= 1
                data = data[:self.length - 1].rstrip() + u'\u2026'
                self.length = 0
            else:
                self.length -= len(data)
            self.parts.append(data)
        else:
            self.truncated = True

    def get_preview(self, data):
        self.parts = []
        self.tag_stack = []
        self.truncated = False
        self.feed(data)
        return (''.join(self.parts), self.truncated)


class BlogEntry(Base):
    __tablename__ = 'blog_entries'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    title = Column(String)
    body = Column(String)
    markup = Column(String)
    public = Column(Boolean)

    def __init__(self):
        self.timestamp = datetime.utcnow()

    def generate_markup(self):
        self.markup = markdown.markdown(
            self.body, output_format='xhtml5', safe_mode='escape')

    def get_preview(self, length, images=0):
        parser = PreviewParser(length, images)
        return parser.get_preview(self.markup)

    def __repr__(self):
        return '<BlogEntry: {}>'.format(self.title)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    series_id = Column(String)
    start = Column(DateTime)
    end = Column(DateTime)
    title = Column(String)
    description = Column(String)
    public = Column(Boolean)

    def __repr__(self):
        return '<Event: {}>'.format(self.title)
