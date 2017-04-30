from functools import wraps
from blog import *

class DeletePost(BlogHandler):
    # Delte the post page
    @user_logged_in
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        # Look up relevant comments
        comments = Comment.query().filter(Comment.post_id == int(post_id)).order(-Comment.created)
        # Pick up these comments
        comment_box = []
        for c in comments:
            comment_box.append(c.key)
        # Check if the editer is logged in and the editer is the author of the post.
        if self.user and self.user.key.id() != post.author.id():
            print "DO NOT Delete... ", self.user.key.id(), post.author.id()
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        else:
            ndb.delete_multi(comment_box)
            key.delete()
            msg = "This post is successfully deleted!"
            self.render('deletepost.html', msg=msg)
