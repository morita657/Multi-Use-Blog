from blog import *

class PostPage(BlogHandler):
    # Write new post if a user is logged in.
    def get(self, post_id, comment=""):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        # Look up comments
        comments = Comment.find_comment_id(post_id)

        if not post:
            self.error(404)
            return

        post._render_text = post.content.replace('\n', '<br>')
        self.render('permalink.html', post = post, comment=comment, comments=comments)
