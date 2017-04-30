from handlers.blog import *
from google.appengine.ext import ndb
# from utils import *

class Comment(ndb.Model):
    comments = ndb.TextProperty(required = True)
    post_id = ndb.IntegerProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    comment_author = ndb.StringProperty(required = True)
    author = ndb.KeyProperty(kind = 'User')

    # Find comment post id
    @classmethod
    def find_comment_id(cls, post_id):
        return Comment.query().filter(Comment.post_id == post_id).get()
