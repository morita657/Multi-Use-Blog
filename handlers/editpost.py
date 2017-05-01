from blog import *

class EditPost(BlogHandler):
    # Go to the specific post page to edit
    @user_logged_in
    @post_exists
    def get(self, post):
        # Edit posts if user id and the author's match, otherwise invoke error message
        if self.user.key.id() != post.author.id():
            error = "You are not allowed to edit this post!"
            self.render('error.html', error=error)
        else:
            self.render('editpost.html', post = post)

    @user_logged_in
    @post_exists
    def post(self, post):
        key = ndb.Key('Post', int(post.key.id()), parent=blog_key())
        post = key.get()
        author = self.user.key.id()
        if self.user.key.id() != post.author.id():
            error = "You're not allowed"
            self.render('error.html', error=error)
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                post.subject = subject
                post.content = content
                post.author = author = ndb.Key('User', int(author))
                post.put()
                self.redirect('/blog/%s' % str(post.key.id()))
            else:
                error = "subject and content, please!"
                self.render('editpost.html', post=post, subject=subject, content=content, error=error)
