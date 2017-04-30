from functools import wraps
from blog import *

class DeletePost(BlogHandler):
    # Delte the post page
    @user_logged_in
    @post_exists
    def get(self, post):
        key = ndb.Key('Post', int(post.key.id()), parent=blog_key())
        post = key.get()
        # Look up relevant comments
        comments = Comment.find_comment_id(post.key.id())
        # Pick up these comments
        comment_box = []
        for c in comments:
            comment_box.append(c.key)
        # Check if the editer is logged in and the editer is the author of the post.
        if self.user.key.id() != post.author.id():
            print "DO NOT Delete... ", self.user.key.id(), post.author.id()
            msg= "You cannot delete this post!"
            self.render('deletepost.html', msg=msg)
        else:
            ndb.delete_multi(comment_box)
            key.delete()
            msg = "This post is successfully deleted!"
            self.render('deletepost.html', msg=msg)
