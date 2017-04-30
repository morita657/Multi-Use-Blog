import os
import re
import random
import hashlib
import hmac
from string import letters
import jinja2
from google.appengine.ext import ndb
from functools import wraps

secret = 'fart'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def users_key(group = 'default'):
    return ndb.Key('users', group)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

# Validations stuff
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

##### blog stuff
def blog_key(name = 'default'):
    return ndb.Key('blogs', name).get()

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

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
            return function(self, post_id, post)
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
            return function(self, post_id, comment)
        else:
            print "404 error"
            self.error(404)
            return
    return wrapper

# # Check if user owns a post
# But how can I use this?
# def user_owns_post(function):
#     @wraps(function)
#     def wrapper(self, post):
#         # key = ndb.Key('Post', int(post_id), parent=blog_key())
#         # post = key.get()
#         return post.author == self.user.key.id()
#     return wrapper
