# Import the Sitemap class from Django's sitemaps framework.
# This class provides the core functionality to generate a sitemap.
from django.contrib.sitemaps import Sitemap

# Import the Post model from the current application's models.py file.
# We need this to get the list of posts to include in the sitemap.
from .models import Post


# Define a new class called PostSitemap that inherits from Django's Sitemap class.
# This class will define the specific sitemap for our blog posts.
class PostSitemap(Sitemap):
    # This attribute tells search engines how frequently the content of post pages changes.
    # Valid values include 'always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', and 'never'.
    changefreq = 'weekly'

    # This attribute indicates the priority of these URLs relative to other URLs on your site.
    # The value is between 0.0 and 1.0. A higher value means higher priority.
    priority = 0.9

    # This method must return a list or QuerySet of objects to be included in the sitemap.
    def items(self):
        # We are returning all posts that have a 'published' status.
        # This assumes the Post model has a custom manager named 'published'.
        return Post.published.all()

    # This method receives each object returned by items() and returns the last
    # time the object was modified.
    def lastmod(self, obj):
        # 'obj' here is an individual Post instance.
        # We return the value from its 'updated' field, which should be a datetime object.
        return obj.updated