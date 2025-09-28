# Django core imports for rendering templates and handling object lookups.
from django.shortcuts import render, get_object_or_404

# Django imports for pagination functionality.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Django's generic class-based view, useful for simple list views (though not used in the final post_list).
from django.views.generic import ListView

# Django decorator to restrict a view to only accept POST requests.
from django.views.decorators.http import require_POST

# Django's mailing functionality.
from django.core.mail import send_mail

# Django's database functions for aggregations like Count.
from django.db.models import Count

# PostgreSQL-specific search functionality from Django.
from django.contrib.postgres.search import SearchVector

# --- Local App Imports ---

# Import models from the current application.
from .models import Post

# Import forms from the current application.
from .forms import EmailPostForm, CommentForm, SearchForm

# Third-party import for tag model from django-taggit.
from taggit.models import Tag


def post_list(request, tag_slug=None):
    """
    Displays a paginated list of published posts.
    
    Optionally filters the posts by a specific tag if a 'tag_slug' is provided in the URL.
    """
    # Start with the base queryset of all published posts using the custom manager.
    post_list = Post.published.all()
    
    # Initialize tag to None. It will hold the Tag object if filtering is active.
    tag = None
    
    # If a tag_slug is provided in the URL, filter the posts by that tag.
    if tag_slug:
        # Retrieve the Tag object or return a 404 error if it doesn't exist.
        tag = get_object_or_404(Tag, slug=tag_slug)
        # Filter the post_list to include only posts that have the specified tag.
        # 'tags__in' is used because a post can have multiple tags.
        post_list = post_list.filter(tags__in=[tag])

    # --- Pagination ---
    # Create a Paginator object to paginate the results, showing 3 posts per page.
    paginator = Paginator(post_list, 3)
    # Get the 'page' parameter from the request's GET parameters. Default to page 1 if not present.
    page_number = request.GET.get('page', 1)
    
    try:
        # Get the requested page of posts.
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., page 99), deliver the last page of results.
        posts = paginator.page(paginator.num_pages)

    # Render the list template, passing the page object and the optional tag object to the context.
    return render(
        request,
        'blog/post/list.html',
        {
            'posts': posts,
            'tag': tag
        }
    )


def post_detail(request, year, month, day, post):
    """
    Displays the detail view for a single post.
    
    Also retrieves and displays active comments, a comment form, and a list of
    similar posts based on shared tags.
    """
    # Retrieve the specific post object based on slug and publication date.
    # get_object_or_404 will raise a 404 error if no matching post is found.
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # Retrieve all active comments for this post.
    comments = post.comments.filter(active=True)
    # Instantiate an empty form for users to add a new comment.
    form = CommentForm()

    # --- Similar Posts Recommendation Logic ---
    # 1. Get a list of IDs for all tags associated with the current post.
    post_tags_ids = post.tags.values_list('id', flat=True)
    # 2. Get all published posts that have at least one of these tags, excluding the current post.
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    # 3. Annotate the queryset with a count of shared tags. 'same_tags' is a new temporary field.
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    # 4. Order the results by the number of shared tags (descending) and then by publish date (descending).
    # Finally, slice the result to get the top 4 most similar posts.
    ).order_by('-same_tags', '-publish')[:4]

    # Render the detail template with the post and all related context data.
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )


def post_share(request, post_id):
    """
    Handles the form for sharing a post via email.
    
    On GET: Displays the form.
    On POST: Validates the form data and sends an email.
    """
    # Retrieve the post to be shared by its ID, ensuring it is a published post.
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    # 'sent' flag is used to show a success message in the template after sending the email.
    sent = False
    
    if request.method == 'POST':
        # If the form is submitted, bind the form to the POST data.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # If the form data is valid, process it.
            cd = form.cleaned_data # Access validated data.
            
            # Build the full URL for the post.
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            # Create the email subject and message body.
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            
            # Send the email using Django's send_mail function.
            # 'from_email=None' will use the DEFAULT_FROM_EMAIL setting.
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            # Set the sent flag to True after the email is sent.
            sent = True
    else:
        # If it's a GET request, create a new, empty form to display.
        form = EmailPostForm()
    
    # Render the share template.
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


# The @require_POST decorator ensures this view only accepts POST requests.
# If a user tries to access this URL with a GET request, it will raise an error (HTTP 405).
@require_POST
def post_comment(request, post_id):
    # First, retrieve the post object that the comment is for.
    # get_object_or_404 is a handy shortcut: it tries to get the object,
    # but if it doesn't exist, it returns a 404 "Not Found" page.
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED # Ensure we only comment on published posts.
    )
    # Initialize the comment variable to None. It will hold the new comment object if creation is successful.
    comment = None

    # Instantiate the CommentForm with the submitted data from the request (request.POST).
    form = CommentForm(data=request.POST)

    # Check if the submitted data is valid according to the form's rules.
    if form.is_valid():
        # Create a Comment object in memory but don't save it to the database yet.
        # `commit=False` is crucial because we need to add the 'post' relationship
        # to the comment object before saving it.
        comment = form.save(commit=False)

        # Assign the retrieved post object to the comment's 'post' foreign key field.
        comment.post = post

        # Now that the comment object has all its required data, save it to the database.
        comment.save()

    # After processing, render a template to show the user the result.
    # We pass the post, the form (which will include error messages if it was invalid),
    # and the newly created comment object to the template context.
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

def post_search(request):
    # Instantiate an empty form object. This will be used to display the form initially.
    form = SearchForm()
    
    # Initialize query and results variables.
    query = None
    results = []

    # Check if the 'query' parameter exists in the request's GET parameters.
    # This indicates that the user has submitted the search form.
    if 'query' in request.GET:
        # If the form was submitted, create a form instance and populate it with data from the request.
        form = SearchForm(request.GET)
        
        # Check whether the form's data is valid.
        if form.is_valid():
            # If the form is valid, get the 'query' from the form's cleaned_data dictionary.
            # cleaned_data contains the validated and sanitized user input.
            query = form.cleaned_data['query']
            
            # Perform the full-text search query.
            # Post.published: Accesses a custom manager on the Post model to get only published posts.
            # .annotate(...): Creates a new temporary field named 'search' for each post in the queryset.
            # SearchVector('title', 'body'): The 'search' field is populated with a search vector
            # combining the 'title' and 'body' fields of the Post model. This vector is optimized for searching.
            # .filter(search=query): Filters the posts, returning only those where the combined 'search' vector
            # matches the user's search 'query'.
            results = Post.published.annotate(
                search=SearchVector('title', 'body'),
            ).filter(search=query)

    # Render the search template with the context.
    # The context dictionary passes the form, the user's query, and the search results to the template.
    return render(request,
                  'blog/post/search.html',
                  {
                      'form': form,
                      'query': query,
                      'results': results
                  }
                 )