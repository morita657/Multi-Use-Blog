from blog import BlogHandler

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')
