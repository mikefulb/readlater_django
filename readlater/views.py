from django.shortcuts import render
from django.views import View, generic

from .models import Article


class ArticleList(generic.ListView):

    # def get(self, request, *args, **kwargs):
    #     return render(request, 'readlater/home.html')

    model = Article
    context_object_name = 'article_list'


class ArticleCreateForm(generic.CreateView):
    model = Article
    fields = ['name', 'url', 'category', 'rank', 'progress']
    template_name_suffix = '_create_form'
