from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View, generic

from .models import Article
from .forms import ArticleCreateForm


class ArticleList(generic.ListView):

    # def get(self, request, *args, **kwargs):
    #     return render(request, 'readlater/home.html')

    model = Article
    context_object_name = 'article_list'

class ArticleCreateView(generic.CreateView):
    model = Article
    form_class = ArticleCreateForm
    #fields = ['name', 'url', 'category']
    template_name_suffix = '_create_form'




# class ArticleCreateView(View):
#     form_class = ArticleCreateForm
#     initial = {'key': 'value'}
#     template_name = 'readlater/article_create_form.html'
#
#     def get(self, request, *args, **kwargs):
#         form = self.form_class(initial=self.initial)
#         print(form)
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             # <process form cleaned data>
#             return HttpResponseRedirect('/success/')
#
#         return render(request, self.template_name, {'form': form})

# class ArticleCreateForm(generic.CreateView):
#     model = Article
#     fields = ['name', 'url', 'category']
#     template_name_suffix = '_create_form'
#
#
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
