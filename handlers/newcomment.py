from models.comment import Comment
from blog import BlogHandler
from utils import *

class NewComment(BlogHandler):
    def post(self, post_id):
        comments = self.request.get('comment')
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        if self.user == "":
            self.redirect('/login')
        elif self.user and self.user.key.id():
            author = self.user.key.id()
            post_id = post.key.id()
            p = Comment(parent = blog_key(), comments=comments, post_id=int(post_id), comment_author=str(self.user.name), author=ndb.Key('User', int(author)))
            p.put()
            self.redirect('/blog/%s' % int(p.post_id))
        else:
            error= "You cannot comment on your post"
            self.render('error.html', error=error)
