from django import forms
#from django.views import generic

from .models import Article


class ArticleCreateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['name', 'url', 'category']


class ArticleEditForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'progress']


# class ArticleDeleteForm(forms.ModelForm):
#
#     class Meta:
#         model = Article
#         fields = ['name', 'url', 'category', 'progress']
