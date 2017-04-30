from models.comment import Comment
from blog import *

class NewComment(BlogHandler):
    @user_logged_in
    @post_exists
    def post(self, post):
        comment = self.request.get('comment')
        key = ndb.Key('Post', int(post.key.id()), parent=blog_key())
        post = key.get()
        # Look up comments
        comments = Comment.find_comment_id(post.key.id())

        if comment == "":
            self.redirect('/blog/%s' % int(post.key.id()))
        else:
            author = self.user.key.id()
            post_id = post.key.id()
            p = Comment(parent = blog_key(), comments=comment, post_id=int(post_id), comment_author=str(self.user.name), author=ndb.Key('User', int(author)))
            p.put()
            self.redirect('/blog/%s' % int(post.key.id()))
