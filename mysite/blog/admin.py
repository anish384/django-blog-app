# Import the admin module from Django's contributions library.
from django.contrib import admin
# Import the Post and Comment models from the current app's models.py file.
from .models import Post, Comment

# The @admin.register() decorator is a clean way to register a ModelAdmin class.
# It performs the same function as admin.site.register(Post, PostAdmin).
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Post model.
    """
    # 'list_display' controls which fields are displayed on the change list page of the admin.
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    
    # 'list_filter' creates a filter sidebar, allowing users to filter results by these fields.
    list_filter = ['status', 'created', 'publish', 'author']
    
    # 'search_fields' adds a search box at the top of the change list,
    # enabling searching through the specified fields.
    search_fields = ['title', 'body']
    
    # 'prepopulated_fields' automatically fills in the slug field as you type in the title field.
    # This is very useful for creating user-friendly URLs.
    prepopulated_fields = {'slug': ('title',)}
    
    # 'raw_id_fields' changes the 'author' field from a dropdown to a lookup widget.
    # This is more efficient than a dropdown when you have thousands of users.
    raw_id_fields = ['author']
    
    # 'date_hierarchy' adds navigation links by date (e.g., by year, month, day) at the top of the change list.
    date_hierarchy = 'publish'
    
    # 'ordering' sets the default sorting order for the objects in the admin list view.
    ordering = ['status', 'publish']
    
    # 'show_facets' displays counts for each filter option in the sidebar (requires Django 4.1+).
    # This shows how many items match each filter without having to click on it.
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Comment model.
    """
    # Displays these fields in the comment list view.
    list_display = ['name', 'email', 'post', 'created', 'active']
    
    # Adds a filter sidebar for 'active' status and the date fields.
    list_filter = ['active', 'created', 'updated']
    
    # Adds a search box to search for comments by the commenter's name, email, or body content.
    search_fields = ['name', 'email', 'body']