from blog import *

class LikePost(BlogHandler):
    # If a user is logged in, she is allowed to like/ dislike a specific post
    # using 'Like' button.
    @user_logged_in
    @post_exists
    def post(self, post):
        key = ndb.Key('Post', int(post.key.id()), parent=blog_key())
        post = key.get()
        if post.author.id() == self.user.key.id():
            error = "You cannot upvoke this post!"
            self.render('error.html', error=error)
        elif post.author.id() != self.user.key.id():
            if not self.user.key.id() in post.like:
                post.like.append(self.user.key.id())
                post.put()
                self.redirect('/blog/%s' % int(post.key.id()))
            elif self.user.key.id() in post.like:
                post.like.remove(self.user.key.id())
                post.put()
                self.redirect('/blog/%s' % int(post.key.id()))
