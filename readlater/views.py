import datetime
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views import View, generic
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse_lazy, reverse

from django.db.models import Max


from .models import Article
from .forms import ArticleCreateForm, ArticleEditForm #, ArticleDeleteForm

# spacing between new entry and lowest rank
RANK_SPACING = 100000


class ArticleList(generic.ListView):
    """ Show unfinished articles """
    model = Article
    #queryset = model.objects.filter(progress__lt=100)
    ordering = ['-category', 'progress', 'rank', '-added_time']
    context_object_name = 'article_list'

    def get(self, request, *args, **kwargs):
        print('get', kwargs)
        # reject invalid state request (read or unread only allowed)
        state = kwargs.get('state')
        if state not in ['read', 'unread', None]:
            raise Http404(f'Invalid article listing state "{state}"! '
                          'Use either "read" or "unread".')

        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs.get('state') == 'read':
            return self.model.objects.filter(progress=100)
        else:
            return self.model.objects.filter(progress__lt=100)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # if state is not defined then default to unread listing
        print('get_context_data')
        print(self.kwargs)
        context['state'] = self.kwargs.get('state') or 'unread'
        return context


class ArticleCreateView(generic.CreateView):
    model = Article
    form_class = ArticleCreateForm
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        """ Add values to instance before saving """
        self.object = form.save(commit=False)

        # set rank to largest value plus spacing between entries
        rank_max = self.model.objects.get_max_rank()
        self.object.rank = rank_max + RANK_SPACING
        self.object.save()
        return super().form_valid(form)


class ArticleEditView(generic.UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """ Add values to instance before saving """
        self.object = form.save(commit=False)
        self.object.updated_time = datetime.datetime.now()
        if self.object.progress == 100:
            self.object.finished_time = datetime.datetime.now()
        else:
            self.object.finished_time = None

        return super().form_valid(form)

    def get_success_url(self):
        # make sure we go back to page that we were called from
        state = self.request.GET.get('state')
        return reverse('article_list_with_state', kwargs={'state': state})

class ArticleDeleteView(generic.DeleteView):
    model = Article
    #form_class = ArticleDeleteForm
    success_url = reverse_lazy('article_list')
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        # make sure we go back to page that we were called from
        print(self.request.POST)
        state = self.request.POST.get('state')
        return reverse('article_list_with_state', kwargs={'state': state})
