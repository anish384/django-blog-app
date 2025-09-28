# Django core imports for building models, handling timezones, accessing settings, and reversing URLs.
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

# Third-party import for adding tagging functionality to the Post model.
# from django-taggit library
from taggit.managers import TaggableManager

# Create your models here

class PublishedManager(models.Manager):
    """
    A custom model manager for the Post model.
    
    This manager returns a QuerySet that only includes posts with a 'PUBLISHED' status.
    This allows for easily querying only the published posts, e.g., Post.published.all().
    """
    def get_queryset(self):
        """
        Overrides the default get_queryset method.
        
        Returns:
            QuerySet: A filtered QuerySet containing only posts with the status 'PUBLISHED'.
        """
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )


class Post(models.Model):
    """
    Represents a single blog post in the database.
    """

    class Status(models.TextChoices):
        """
        An enumeration for the status of a blog post.
        
        - DRAFT: The post is being written and is not yet visible to the public.
        - PUBLISHED: The post is finished and visible on the website.
        """
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    # --- Post Fields ---

    # The title of the blog post.
    title = models.CharField(max_length=250)
    
    # A URL-friendly slug for the post's URL.
    # 'unique_for_date' ensures that no two posts have the same slug on the same publish date.
    slug = models.SlugField(
        max_length=250,
        unique_for_date='publish'
    )
    
    # A foreign key to the user model, representing the author of the post.
    # settings.AUTH_USER_MODEL is used to refer to the project's user model.
    # on_delete=models.CASCADE means if the author (user) is deleted, their posts are also deleted.
    # related_name='blog_posts' allows accessing a user's posts via user.blog_posts.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    
    # The main content/body of the blog post.
    body = models.TextField()

    # --- Timestamps and Status ---
    
    # The date and time the post is scheduled to be published. Defaults to the current time.
    publish = models.DateTimeField(default=timezone.now)
    
    # The timestamp for when the post was created. Automatically set when the object is first created.
    created = models.DateTimeField(auto_now_add=True)
    
    # The timestamp for the last time the post was updated. Automatically updated on save.
    updated = models.DateTimeField(auto_now=True)
    
    # The publication status of the post, chosen from the Status choices. Defaults to 'Draft'.
    status = models.CharField(
        max_length=2,
        choices=Status.choices,  # Use '.choices' to get the tuple pairs for the choices option
        default=Status.DRAFT
    )

    # --- Model Managers ---

    # The default manager for the model, allowing queries like Post.objects.all().
    objects = models.Manager() 
    
    # The custom manager to retrieve only published posts, e.g., Post.published.all().
    published = PublishedManager() 

    # The tag manager from django-taggit, allowing for tagging functionality.
    tags = TaggableManager()

    # --- Metadata and Methods ---

    class Meta:
        """
        Metadata options for the Post model.
        """
        # Default ordering for query results: descending by publish date.
        # The '-' indicates descending order. Newest posts will appear first.
        ordering = ['-publish']
        
        # Database indexes to improve query performance.
        # This index speeds up queries that filter or order by the 'publish' field.
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        """
        Returns a string representation of the Post object, which is its title.
        This is used in the Django admin site and other places where the object is displayed as a string.
        """
        return self.title
    
    def get_absolute_url(self):
        """
        Returns the canonical URL for a post instance.
        
        This is a Django convention used by various components (like the admin site)
        to link to the detailed view of an object. The 'reverse' function builds the URL
        based on the URL pattern name 'blog:post_detail' and the provided arguments.
        """
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )

# comments model
class Comment(models.Model):
    # --- Fields ---
    # This field creates a many-to-one relationship with the 'Post' model.
    # Each comment is linked to a single post.
    post = models.ForeignKey(
        Post,
        # on_delete=models.CASCADE ensures that if a post is deleted,
        # all comments associated with it are also deleted.
        on_delete=models.CASCADE,
        # 'related_name' allows us to easily access the set of comments from a Post object.
        # For example, you can use `post.comments.all()` to get all comments for a specific post.
        related_name='comments'
    )
    
    # A character field to store the name of the commenter. Maximum length is 80 characters.
    name = models.CharField(max_length=80)
    
    # An email field that validates the input is a proper email format.
    email = models.EmailField()
    
    # A text field for the main content of the comment. It can hold a large amount of text.
    body = models.TextField()
    
    # A date and time field to store when the comment was created.
    # `auto_now_add=True` automatically sets this to the current timestamp when a comment is first created.
    # It won't be updated on subsequent saves.
    created = models.DateTimeField(auto_now_add=True)
    
    # A date and time field to store the last update time of the comment.
    # `auto_now=True` automatically updates this to the current timestamp every time the comment is saved.
    updated = models.DateTimeField(auto_now=True)
    
    # A boolean field to easily enable or disable a comment (useful for moderation).
    # `default=True` means all new comments will be active unless manually deactivated.
    active = models.BooleanField(default=True)

    # --- Metadata ---
    # The 'Meta' inner class holds configuration options for the model.
    class Meta:
        # `ordering` specifies the default order for query results.
        # Here, `['created']` means comments will be sorted by their creation date, from oldest to newest.
        ordering = ['created']
        
        # `indexes` tells the database to create an index on certain fields.
        # An index on the 'created' field can make filtering or ordering by this field much faster.
        indexes = [
            models.Index(fields=['created']),
        ]

    # --- Methods ---
    # The `__str__` method defines how a model instance is represented as a string.
    # This is very helpful in the Django admin site and for debugging.
    def __str__(self):
        # This will return a descriptive string, e.g., "Comment by John Doe on My First Post"
        return f'Comment by {self.name} on {self.post}'
