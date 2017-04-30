from blog import BlogHandler
from models.post import Post
from utils import *

class NewPost(BlogHandler):
    # Create new post to fill in a subject and content field while a user is logging in.
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        author = self.user.key.id()

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, author=ndb.Key('User', int(author)))
            p.put()
            self.redirect('/blog/%s' % str(p.key.id()))
        else:
            error = "subject and content, please!"
            self.render('newpost.html', subject=subject, content=content, error=error)
