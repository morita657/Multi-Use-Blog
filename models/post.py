from google.appengine.ext import ndb
from functools import wraps
from utils import *
from handlers.blog import *
from models.comment import Comment

class Post(ndb.Model):
    subject = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    author = ndb.KeyProperty(kind = 'User')
    like = ndb.IntegerProperty(repeated=True)

    @property
    def like_by(self):
        return len(self.like)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)
