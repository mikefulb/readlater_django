from django.urls import path

from . import views

urlpatterns = [
    path('', views.ArticleList.as_view(), name='article_list'),
    path('article/create/new', views.ArticleCreateForm.as_view(), name='article_create_form'),
    # path('projects/', views.ProjectList.as_view(), name='projects-list'),
    # path('projects/<int:project_id>/', views.project, name='project-summary'),
    # path('requests/<int:request_id>/', views.request, name='request')
]
