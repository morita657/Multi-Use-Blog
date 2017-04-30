from blog import *

class EditComment(BlogHandler):
    # Edit comment if the comment is written by same author.
    @user_logged_in
    @comment_exists
    def get(self, post_id, comment):

        key = ndb.Key('Comment', int(post_id), parent=blog_key())
        comment = key.get()
        if self.user.key.id() == comment.author.id():
            self.render('editcomment.html', comment=comment)
        else:
            error = "You are not allowed to edit this comment!"
            self.render('error.html', error=error)

    def post(self, post_id):
        key = ndb.Key('Comment', int(post_id), parent=blog_key())
        post = key.get()

        comment = self.request.get('comment')
        author = self.user.key.id()

        if comment:
            post.comments = comment
            post.post_id = int(post.post_id)
            post.comment_author = str(self.user.name)
            post.author = ndb.Key('User', int(author))
            post.put()
            self.redirect('/blog/%s' % int(post.post_id))
        else:
            error = "Don't forget to fill in input field!"
            self.render('editcomment.html', comment=comment, error=error)
