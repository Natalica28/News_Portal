from django import forms
from .models import Post
class PostForm(forms.ModelForm):
   class Meta:
       model = Post
       fields = ['author', 'choice_category', 'head', 'text']