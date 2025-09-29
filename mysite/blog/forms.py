# Import the forms module from Django
from django import forms
# Import the Comment model from the local models.py file
from .models import Comment
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# This is a standard Django form, not tied to a specific model.
class EmailPostForm(forms.Form):
    # A text input for the sender's name with a max length of 50 characters.
    name = forms.CharField(max_length=50)
    # An input that validates for a correct email format.
    email = forms.EmailField()
    # An input for the recipient's email, which also validates the format.
    to = forms.EmailField()
    # A multi-line text area for comments.
    comments = forms.CharField(
        # This field is optional.
        required=False,
        # This tells Django to render the field as a <textarea> HTML element.
        widget=forms.Textarea
    )


# This is a ModelForm, which builds a form directly from a model.
class CommentForm(forms.ModelForm):
    # The 'Meta' class provides configuration for the form.
    class Meta:
        # **model = Comment**: Tells the form which model to use.
        model = Comment
        # **fields = [...]**: Specifies exactly which fields from the Comment model
        # should be included in the form. Django will automatically create
        # the appropriate form fields (e.g., CharField for 'name', TextField for 'body').
        fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
    query = forms.CharField()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'tags', 'status'] # Add all fields a user can edit

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')