from google.appengine.ext import ndb
from functools import wraps

from utils import *

# Decorator
# Check if a user is logged in.
def user_logged_in(function):
    @wraps(function)
    def wrapper(self, post_id):
        if self.user:
            return function(self, post_id)
        else:
            self.redirect('/login')
    return wrapper

# Check if a post exists.
def post_exists(function):
    @wraps(function)
    def wrapper(self, post_id):
        key = ndb.Key('Post', int(post_id))
        post = key.get()
        if post:
            return function(self, post)
        else:
            print "404 error"
            self.error(404)
            return
    return wrapper

# Check if a comment exists.
def comment_exists(function):
    @wraps(function)
    def wrapper(self, post_id):
        key = ndb.Key('Comment', int(post_id), parent=blog_key())
        comment = key.get()
        if comment:
            return function(self, comment)
        else:
            print "404 error"
            self.error(404)
            return
    return wrapper

# Check if user owns a post
def user_owns_post(function):
    @wraps(function)
    def wrapper(self, post):
        return post.author == self.user.key.id()
    return wrapper
