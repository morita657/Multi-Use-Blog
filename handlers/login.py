from utils import *
from handlers.blog import *
from models.user import User

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
