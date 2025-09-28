# Import the markdown library to convert Markdown syntax to HTML.
import markdown

# Import the base Feed class from Django's syndication framework.
from django.contrib.syndication.views import Feed

# Import a template filter to safely truncate HTML content without breaking tags.
from django.template.defaultfilters import truncatewords_html

# Import reverse_lazy to generate URLs from URL names. It's the "lazy" version,
# meaning it won't execute until the value is needed, which is necessary here.
from django.urls import reverse_lazy

# Import the Post model, which contains the data for our feed items.
from .models import Post


# Define a custom feed class that inherits from Django's Feed class.
class LatestPostsFeed(Feed):
    # The title of the feed, which appears in feed readers.
    # Corresponds to the <title> element in the RSS feed.
    title = 'My blog'

    # The main link for the feed, which usually points to the website's homepage or blog index.
    # 'blog:post_list' is the URL name for the main post list view.
    # Corresponds to the <link> element.
    link = reverse_lazy('blog:post_list')

    # A brief description of the feed's content.
    # Corresponds to the <description> element.
    description = 'New posts of my blog.'

    # This method returns the list of objects that will be included in the feed as items.
    def items(self):
        # We retrieve the 5 most recent published posts.
        return Post.published.all()[:5]

    # This method is called for each object in items() to get the title for that item.
    # The 'item' argument here is a Post object.
    def item_title(self, item):
        return item.title

    # This method is called for each object to get the description for that item.
    def item_description(self, item):
        # 1. Convert the post's body from Markdown to HTML.
        # 2. Truncate the resulting HTML to the first 30 words.
        # 3. truncatewords_html ensures that any HTML tags are properly closed.
        return truncatewords_html(markdown.markdown(item.body), 30)

    # This method is called for each object to get its publication date.
    def item_pubdate(self, item):
        # Return the 'publish' datetime object from the Post model.
        return item.publish