from blog import *

class EditComment(BlogHandler):
    # Edit comment if the comment is written by same author.
    @user_logged_in
    @comment_exists
    def get(self, comment):

        key = ndb.Key('Comment', int(comment.key.id()), parent=blog_key())
        comment = key.get()
        if self.user.key.id() == comment.author.id():
            self.render('editcomment.html', comment=comment)
        else:
            error = "You are not allowed to edit this comment!"
            self.render('error.html', error=error)

    @user_logged_in
    @comment_exists
    def post(self, comments):
        key = ndb.Key('Comment', int(comments.key.id()), parent=blog_key())
        comment_post = key.get()

        comment = self.request.get('comment')
        author = self.user.key.id()

        if comment and comment_post.author.id() == self.user.key.id():
            comment_post.comments = comment
            comment_post.post_id = int(comment_post.post_id)
            comment_post.comment_author = str(self.user.name)
            comment_post.author = ndb.Key('User', int(author))
            comment_post.put()
            self.redirect('/blog/%s' % int(comment_post.post_id))
        else:
            error = "Don't forget to fill in input field!"
            self.render('editcomment.html', comment=comment, error=error)
