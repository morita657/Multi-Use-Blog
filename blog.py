import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'fart'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        print "Logged in... uid and user_id", str(user.key().id())

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Udacity!')


##### user stuff
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

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    author = db.IntegerProperty(required = True)

    def render(self):

        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class Comment(db.Model):
    comments = db.StringProperty(required = True)
    post_id = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    comment_author = db.StringProperty(required = True)


class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')

        self.render('front.html', posts = posts)


class PostPage(BlogHandler):
    def get(self, post_id, comment=""):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # Look up comments
        comments = Comment.all().filter('post_id =', int(post_id))

        data = []
        for c in comments:
            data.append(c)
            print "data: ", data
        # print "PPOST: ", self.user.key().id()

        if not post:
            self.error(404)
            return

        post._render_text = post.content.replace('\n', '<br>')
        self.render("permalink.html", post = post, comment=comment, comments=data)

    def post(self, post_id):
        comments = self.request.get('comment')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        print "putting...", comments

        if self.user:
            p = Comment(parent = key, comments=comments, post_id=int(post_id), comment_author=str(self.user.name))
            p.put()
            self.redirect('/blog/%s' % int(post_id))
        else:
            self.redirect('/login')

class EditComment(BlogHandler):
    def get(self, post_id):
        # key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        # post = db.get(key)
        # Look up comments
        # print "This is comment something... ", comment.by_id()
        # print "post...", post_id
        comments = Comment.all().filter('post_id =', int(post_id))
        for d in comments:
            # print "print d: ", d, d.comments
            # print "post_id: ", d.post_id, d.key().id()
            print "Pint comment: ", d.comments
            print "Print comment id: ", d.key().id()

        self.render('editcomment.html', comments=d.comments)

    def post(self, post_id):
        comments = self.request.get('comment')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        p = Comment(parent = key, comments=comments, post_id=int(post_id), comment_author=str(self.user.name))
        p.put()
        self.redirect('/blog/%s' % int(post_id))


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        uid = self.read_secure_cookie('user_id')
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        author = self.user.key().id()

        if subject and content:
            print "NewPost... ", self.user.key().id(), int(uid)
            p = Post(parent = blog_key(), subject = subject, content = content, author=int(author))
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

# class Unit2Signup(Signup):
#     def done(self):
#         self.redirect('/unit2/welcome?username=' + self.username)

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            print "Show user info... ", u
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

# class Unit3Welcome(BlogHandler):
#     def get(self):
#         if self.user:
#             self.render('welcome.html', username = self.user.name)
#         else:
#             self.redirect('/signup')

class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')

class EditPost(BlogHandler):
    # Go to the specific post page to edit
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        # print "heyy...", self.user.key().id(), post.author, post_id
        print "this is edit post page...: ", post_id

        # Edit posts if user id and the author's match, otherwise invoke error message
        print "Check user... ", self.user
        if self.user == "":
            self.redirect('/login')
        elif self.user and self.user.key().id() != post.author:
            print "self.user.key().id(): ", self.user.key().id()
            error = "You are not allowed to edit this post!"
            self.write(error)
        else:
            self.render('editpost.html', post = post)

        # If the specific post does not exist return 404
        if not post:
            self.error(404)
            return

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if self.user == "":
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        elif self.user and self.user.key().id() != post.author:
            error = "You're not allowed"
            self.write(error=error)
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                p = Post(parent = blog_key(), subject = subject, content = content, author=int(post.author))
                p.put()
                self.redirect('/blog/%s' % str(p.key().id()))
            else:
                error = "subject and content, please!"
                self.render("editpost.html", post=post, subject=subject, content=content, error=error)

class DeletePost(BlogHandler):
    # Delte the post page
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        # Check if the editer is logged in and the editer is the author of the post.
        if self.user == "":
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        elif self.user and self.user.key().id() != post.author:
            print "DO NOT Delete... ", self.user.key().id()
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        else:
            # print "Delete... ", self.user.key().id()
            db.delete(key)
            msg = "This post is successfully deleted!"
            self.render('deletepost.html', msg=msg)



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
                               ('/blog/editpost/(\d+)', EditPost),
                               ('/blog/deletepost/(\d+)', DeletePost),
                            #    ('/blog/([0-9]+)', CommentPost),
                               ('/blog/editcomment/(\d+)', EditComment),
                               ],
                              debug=True)
