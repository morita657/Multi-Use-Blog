import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2
import wsgiref.handlers
from google.appengine.ext import ndb
from functools import wraps


from utils import *
from decorators import *

from handlers.blog import *
from handlers.signup import Register
from handlers.login import Login
from handlers.logout import Logout
from handlers.newpost import NewPost
from handlers.newcomment import NewComment
from handlers.editcomment import EditComment
from handlers.deletecomment import DeleteComment
from handlers.likepost import LikePost
from handlers.editpost import EditPost
from handlers.deletepost import DeletePost
from handlers.permalink import PostPage

from models.user import User
from models.post import Post
from models.comment import Comment

app = webapp2.WSGIApplication([('/', MainPage),
                            #    ('/unit2/rot13', Rot13),
                            #    ('/unit2/signup', Unit2Signup),
                               ('/unit2/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                            #    ('/unit3/welcome', Unit3Welcome),
                               ('/blog/comment/(\d+)', NewComment),
                               ('/blog/editpost/(\d+)', EditPost),
                               ('/blog/deletepost/(\d+)', DeletePost),
                            #    ('/blog/([0-9]+)', CommentPost),
                               ('/blog/editcomment/(\d+)', EditComment),
                               ('/blog/deletecomment/(\d+)', DeleteComment),
                               ('/blog/liked/(\d+)', LikePost),
                               ],
                              debug=True)
