import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
import markdown
from ricecrew.database import Base


class BlogEntry(Base):
    __tablename__ = 'blog_entries'

    id = Column(Integer, primary_key=True)
    date_posted = Column(DateTime)
    title = Column(String)
    body = Column(String)
    markup = Column(String)
    public = Column(Boolean)

    def generate_markup(self):
        self.markup = markdown.markdown(
            self.body, output_format='xhtml5', safe_mode='escape')

    def __repr__(self):
        return '<BlogEntry: {}>'.format(self.title)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    title = Column(String)
    description = Column(String)
    public = Column(Boolean)

    def __repr__(self):
        return '<Event: {}>'.format(self.title)
