from blog import *

class DeleteComment(BlogHandler):
    # A user is allowed to delete a post if she is logged in and the post is
    # made by her.
    @user_logged_in
    def get(self, post_id):
        if self.user:
            key = ndb.Key('Comment', int(post_id), parent=blog_key())
            comment = key.get()
            if self.user.name == comment.comment_author:
                key.delete()
                msg = "This comment is successfully deleted!"
                self.render('deletecomment.html', msg=msg)
            else:
                error = "You are not allowed to delete this comment!"
                self.render('error.html', error=error)
