# Import the default admin site and the path function for URL routing.
from django.contrib import admin
from blog import views as blog_views 
from django.urls import path, include

# Import the sitemap view from Django's sitemaps framework.
# This view is responsible for generating the sitemap XML file.
from django.contrib.sitemaps.views import sitemap

# Import your custom PostSitemap class from the sitemaps.py file in your blog app.
from blog.sitemaps import PostSitemap

# Create a dictionary to hold all the sitemaps for your site.
# The keys of this dictionary (e.g., 'posts') are used to name the sitemap sections.
# The values are instances of your Sitemap classes.
sitemaps = {
    'posts': PostSitemap,
}

# Define the URL patterns for your project.
urlpatterns = [
    # URL for the Django admin interface.
    path('admin/', admin.site.urls),

    # Include the URLs from your blog application, prefixed with 'blog/'.
    # path('', include('blog.urls', namespace='blog')),

    path('accounts/', include('django.contrib.auth.urls')),

    # Define the URL for the sitemap.
    # When a user or search engine requests /sitemap.xml, Django will use the 'sitemap' view.
    # The view is passed the 'sitemaps' dictionary, so it knows which sitemap
    # configurations to use to generate the XML content.
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

        # 1. New path for the homepage (the root URL)
    
    # 2. Changed path for the blog app (now at /blog/)
    path('', include('blog.urls', namespace='blog')),

    path('accounts/register/', blog_views.register, name='register'),
]
