from django import forms
#from django.views import generic

from .models import Article


class ArticleCreateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['name', 'url', 'category']
        #template_name_suffix = '_create_form'


# class ArticleEditForm(generic.CreateView):
#     model = Article
#     fields = ['name', 'url', 'category', 'rank', 'progress']
#     template_name_suffix = '_create_form'
#
#
# class ArticleDeleteForm(generic.CreateView):
#     model = Article
#     fields = ['name', 'url', 'category', 'rank', 'progress']
#     template_name_suffix = '_create_form'
