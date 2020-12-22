import datetime

from django.http import Http404
from django.views import generic
from django.urls import reverse_lazy, reverse

from .models import Article
from .models import Category
from .forms import ArticleCreateForm, ArticleEditForm
from .forms import CategoryCreateForm, CategoryEditForm


class ArticleList(generic.ListView):
    """ Show unfinished articles """
    model = Article
    context_object_name = 'article_list'

    # default field to order by if no valid no given
    _order_field = 'priority'

    _order_hier = {
            'priority': ('priority',  '-progress'),
            'category': ('-category', 'priority', 'updated_time', '-added_time', '-progress'),
            'progress': ('-progress', 'priority', 'updated_time', '-added_time', '-category'),
    }

    @staticmethod
    def _clean_order_col(order_col):
        """ Remove any ordering punctuation from a order column specification"""
        return order_col.strip('-')

    def _get_order_col_via_url(self, clean=True):
        """
        Return field to order list of articles by.
        If field name is preceded by a '-' then order of list is reversed.
        Specify clean=True to remove this extra punctuation otherwise it will be left on the name.

        :param clean: If True clean parameter or any punctuation.
        :type clean: bool
        :return: Field name to order list by.
        :rtype: str
        """
        # pull ordering field from GET if present
        order_col = self.request.GET.get('orderby', self._order_field)

        # test it is a valid option or set a default
        # strip off '-' at front of field name used to change order of sort
        # FIXME is this best way or should this be all inside the model or model manager
        if not getattr(Article, order_col.strip('-'), None):
            order_col = self._order_field

        if clean:
            order_col = self._clean_order_col(order_col)

        return order_col

    def get(self, request, *args, **kwargs):
        # reject invalid state request (read or unread only allowed)
        state = kwargs.get('state')
        if state not in ['read', 'unread', None]:
            raise Http404(f'Invalid article listing state "{state}"! '
                          'Use either "read" or "unread".')

        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        order_col = self._get_order_col_via_url(clean=False)

        # find secondary ordering priorities if any
        order_hier = self._order_hier.get(self._clean_order_col(order_col),
                                          (order_col,))
        if self.kwargs.get('state') == 'read':
            return self.model.objects.filter(progress=100).order_by(*order_hier)
        else:
            return self.model.objects.filter(progress__lt=100).order_by(*order_hier)

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # if state is not defined then default to unread listing
        context['state'] = self.kwargs.get('state') or 'unread'

        # see if any list ordering specified
        context['order_col'] = self._get_order_col_via_url()

        return context


class ArticleCreateView(generic.CreateView):
    model = Article
    form_class = ArticleCreateForm
    template_name_suffix = '_create_form'

    # def form_valid(self, form):
    #     """ Add values to instance before saving """
    #     self.object = form.save(commit=False)
    #
    #     # set rank to largest value plus spacing between entries
    #     rank_max = self.model.objects.get_max_rank()
    #     self.object.rank = rank_max + RANK_SPACING
    #     self.object.save()
    #     return super().form_valid(form)


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
    success_url = reverse_lazy('article_list')
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        # make sure we go back to page that we were called from
        state = self.request.POST.get('state')
        return reverse('article_list_with_state', kwargs={'state': state})


class SettingsView(generic.base.TemplateView):
    template_name = 'readlater/settings_base.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # if state is not defined then default to unread listing
        context['category_list'] = Category.objects.all().order_by('name')

        return context


class CategoryCreateView(generic.CreateView):
    model = Category
    form_class = CategoryCreateForm
    success_url = reverse_lazy('settings')
    template_name_suffix = '_create_form'


class CategoryEditView(generic.UpdateView):
    model = Category
    form_class = CategoryEditForm
    success_url = reverse_lazy('settings')
    template_name_suffix = '_edit_form'


class CategoryDeleteView(generic.DeleteView):
    model = Category
    success_url = reverse_lazy('settings')
    template_name_suffix = '_delete_form'
