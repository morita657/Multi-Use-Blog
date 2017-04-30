from blog import *

class LikePost(BlogHandler):
    # If a user is logged in, she is allowed to like/ dislike a specific post
    # using 'Like' button.
    def post(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        if self.user == "":
            self.redirect("/signup")
        elif self.user and post.author == self.user.key.id():
            print "post author: ", post.author
            print "user key id: ", self.user.key.id()
            error = "You cannot upvoke this post!"
            self.render('error.html', error=error)
        elif  self.user and post.author != self.user.key.id():
            if not self.user.key.id() in post.like:
                print "post author: ", post.author
                print "user key id: ", self.user.key.id()
                print "user name: ", self.user.name
                post.like.append(self.user.key.id())
                post.put()
                self.redirect('/blog/%s' % int(post_id))
            elif self.user.key.id() in post.like:
                post.like.remove(self.user.key.id())
                post.put()
                print "post author: ", post.author
                print "user key id: ", self.user
                print "user name: ", self.user.name
                print "like array: ", post.like
                self.redirect('/blog/%s' % int(post_id))
