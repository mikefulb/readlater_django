from django.contrib import admin
from django.urls import path, include
#from decouple import config
from readlater_django.utils import load_env

urlpatterns = [
    path('readlater/', include('readlater.urls')),
    path(load_env('ADMIN_SECRET_URL'), admin.site.urls),
]
