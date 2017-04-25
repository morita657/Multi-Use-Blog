import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import ndb

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
        self.set_secure_cookie('user_id', str(user.key.id()))
        print "Logged in... uid and user_id", str(user.key.id())

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
    return ndb.Key('users', group)

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.query().filter(User.name == name).get()
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
    return ndb.Key('blogs', name).get()


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

class Comment(ndb.Model):
    comments = ndb.TextProperty(required = True)
    post_id = ndb.IntegerProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    comment_author = ndb.StringProperty(required = True)
    author_id = ndb.IntegerProperty(required = True)

    # Find comment post id
    @classmethod
    def find_comment_id(cls, post_id):
        return Comment.query().filter(Comment.post_id == post_id).get()


class BlogFront(BlogHandler):
    def get(self):
        # Check if this works...
        # posts = greetings = Post.all().order('-created')
        posts = greetings = Post.query().order(-Post.created)

        self.render('front.html', posts = posts)


class PostPage(BlogHandler):
    # Write new post if a user is logged in.
    def get(self, post_id, comment=""):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        # Look up comments
        comments = Comment.query().filter(Comment.post_id == int(post_id)).order(-Comment.created)

        if not post:
            self.error(404)
            return
        print "user name", self.user.name

        post._render_text = post.content.replace('\n', '<br>')
        self.render('permalink.html', post = post, comment=comment, comments=comments)

    # def post(self, post_id):
    #     comments = self.request.get('comment')
    #     key = ndb.Key('Post', int(post_id), parent=blog_key())
    #     post = key.get()
    #
    #     # print "putting...", post.author, self.user.key.id()
    #     if self.user == "":
    #         self.redirect('/login')
    #     elif self.user.key.id():
    #         p = Comment(parent = blog_key(), comments=comments, post_id=int(post_id), comment_author=str(self.user.name), author_id=int(self.user.key.id()))
    #         p.put()
    #         self.redirect('/blog/%s' % int(p.post_id))
    #     else:
    #         error= "You cannot comment on your post"
    #         self.render('error.html', error=error)

class NewComment(BlogHandler):
    def post(self, post_id):
        comments = self.request.get('comment')
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        # print "putting...", post.author, self.user.key.id()
        if self.user == "":
            self.redirect('/login')
        elif self.user.key.id():
            p = Comment(parent = blog_key(), comments=comments, post_id=int(post_id), comment_author=str(self.user.name), author_id=int(self.user.key.id()))
            p.put()
            self.redirect('/blog/%s' % int(p.post_id))
        else:
            error= "You cannot comment on your post"
            self.render('error.html', error=error)


class EditComment(BlogHandler):
    # Edit comment if the comment is written by same author.
    def get(self, post_id):
        if self.user == "":
            self.redirect("/login")
        elif self.user:
            key = ndb.Key('Comment', int(post_id), parent=blog_key())
            comment = key.get()
            print "this is author id ", self.user.key.id()
            if self.user.name == comment.comment_author:
                self.render('editcomment.html', comment=comment)
            else:
                error = "You are not allowed to edit this comment!"
                self.render('error.html', error=error)

    def post(self, post_id):
        key = ndb.Key('Comment', int(post_id), parent=blog_key())
        post = key.get()

        print "post id is... ", post.post_id
        comment = self.request.get('comment')
        author = self.user.name
        print "post button clicked... ", comment

        if comment:
            post.comments = comment
            post.post_id = int(post.post_id)
            post.comment_author = str(author)
            post.author_id = int(self.user.key.id())
            post.put()
            self.redirect('/blog/%s' % int(post.post_id))
        else:
            error = "Don't forget to fill in input field!"
            self.render('editcomment.html', comment=comment, error=error)

class DeleteComment(BlogHandler):
    # A user is allowed to delete a post if she is logged in and the post is
    # made by her.
    def get(self, post_id):
        if self.user == "":
            self.redirect("/login")
        elif self.user:
            key = ndb.Key('Comment', int(post_id), parent=blog_key())
            comment = key.get()
            if self.user.name == comment.comment_author:
                key.delete()
                msg = "This comment is successfully deleted!"
                self.render('deletecomment.html', msg=msg)
            else:
                error = "You are not allowed to delete this comment!"
                self.render('error.html', error=error)

class LikePost(BlogHandler):
    # If a user is logged in, she is allowed to like/ dislike a specific post
    # using 'Like' button.
    def post(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        if self.user == "":
            self.redirect("/signup")
        elif self.user and post.author == self.user.key.id():
            print "post author: ", post.author
            print "user key id: ", self.user.key.id()
            error = "You cannot upvoke this post!"
            self.render('error.html', error=error)
        elif  self.user and post.author != self.user.key.id():
            if not self.user.key.id() in post.like:
                print "post author: ", post.author
                print "user key id: ", self.user.key.id()
                print "user name: ", self.user.name
                post.like.append(self.user.key.id())
                post.put()
                self.redirect('/blog/%s' % int(post_id))
            elif self.user.key.id() in post.like:
                post.like.remove(self.user.key.id())
                post.put()
                print "post author: ", post.author
                print "user key id: ", self.user
                print "user name: ", self.user.name
                print "like array: ", post.like
                self.redirect('/blog/%s' % int(post_id))


class NewPost(BlogHandler):
    # Create new post to fill in a subject and content field while a user is logging in.
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect("/login")

    def post(self):
        # uid = self.read_secure_cookie('user_id')
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        author = self.user.key.id()
        print "NewPost... ", self.user.key.id()

        if subject and content:
            print "NewPost... ", self.user.key.id()
            # TODO: Find a way to save author
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key.id()))
        else:
            error = "subject and content, please!"
            self.render('newpost.html', subject=subject, content=content, error=error)


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
        self.render('signup-form.html')

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
    # Log in the blog.
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
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        commentt = Comment.get_by_id(int(post_id))
        # print "heyy...", self.user.key.id(), post.author, post_id
        # print "this is edit post page...: ", post_id, commentt, post
        print "SHow post data... ", post


        # Edit posts if user id and the author's match, otherwise invoke error message
        print "Check user... ", self.user
        print "user id... ", self.user.key.id()
        print "post id... ", post.key
        if self.user == "":
            self.redirect('/login')
        elif self.user and self.user.key.id() != post.author:
            # print "self.user.key.id(): ", self.user.key.id()
            error = "You are not allowed to edit this post!"
            self.render('error.html', error=error)
        else:
            self.render('editpost.html', post = post)

        # If the specific post does not exist return 404
        if not post:
            self.error(404)
            return

    def post(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        if self.user == "":
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        elif self.user and self.user.key.id() != post.author:
            error = "You're not allowed"
            self.render('error.html', error=error)
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                post.subject = subject
                post.content = content
                post.author = int(post.author)
                post.put()
                self.redirect('/blog/%s' % str(post.key.id()))
            else:
                error = "subject and content, please!"
                self.render('editpost.html', post=post, subject=subject, content=content, error=error)

class DeletePost(BlogHandler):
    # Delte the post page
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        # Check if the editer is logged in and the editer is the author of the post.
        if self.user == "":
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        elif self.user and self.user.key.id() != post.author:
            print "DO NOT Delete... ", self.user.key.id()
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        else:
            key.delete()
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
                               ('/blog/deletecomment/(\d+)', DeleteComment),
                               ('/blog/liked/(\d+)', LikePost),
                               ('/blog/comment/(\d+)', NewComment),
                               ],
                              debug=True)
