from django import forms
#from django.views import generic

from .models import Article


class ArticleCreateForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'notes']


class ArticleEditForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'progress', 'notes']


# class ArticleDeleteForm(forms.ModelForm):
#
#     class Meta:
#         model = Article
#         fields = ['name', 'url', 'category', 'progress']
