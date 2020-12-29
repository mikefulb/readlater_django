from django.urls import path, include
from django.views.generic.base import RedirectView
from . import views


#
# URLs explanations
#
# '' - root of site is list of articles.  Each article item in list has links to
#      visit the article URL, as well as edit or delete the article from the list
#
# 'article/create/new' - Create a new article entry in the database.
#                        When successful return to root page
#
# 'article/edit/<int:pk> - Edit the article in database with private key == pk.
#                          When successful return to root page.
#
# 'article/delete/<int:pk> - Handles deleting the article in database with private key == pk.
#                          When successful return to root page.
#
#

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='article_list'), name='home'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('category/create/new', views.CategoryCreateView.as_view(), name='category_create_form'),
    path('category/edit/<int:pk>', views.CategoryEditView.as_view(), name='category_edit_form'),
    path('category/delete/<int:pk>', views.CategoryDeleteView.as_view(), name='category_delete_form'),
    path('articles/', views.ArticleList.as_view(), name='article_list'),
    path('articles/<str:state>', views.ArticleList.as_view(), name='article_list_with_state'),
    path('article/create/new', views.ArticleCreateView.as_view(), name='article_create_form'),
    path('article/edit/<int:pk>', views.ArticleEditView.as_view(), name='article_edit_form'),
    path('article/delete/<int:pk>', views.ArticleDeleteView.as_view(), name='article_delete_form'),
    path('accounts/', include('django.contrib.auth.urls')),

]
