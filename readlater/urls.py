from django.urls import path

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
    path('', views.ArticleList.as_view(), name='article_list'),
    path('article/create/new', views.ArticleCreateView.as_view(), name='article_create_form'),
#    path('article/edit/<int:pk>', views.ArticleEditForm.as_view(), name='article_edit_form'),
#    path('article/delete/<int:pk>>', views.ArticleDeleteForm.as_view(), name='article_delete_form'),
    # path('projects/', views.ProjectList.as_view(), name='projects-list'),
    # path('projects/<int:project_id>/', views.project, name='project-summary'),
    # path('requests/<int:request_id>/', views.request, name='request')
]
