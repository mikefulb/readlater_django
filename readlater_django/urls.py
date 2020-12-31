from django.contrib import admin
from django.urls import path, include
from decouple import config

urlpatterns = [
    path('readlater/', include('readlater.urls')),
    path(config('ADMIN_SECRET_URL'), admin.site.urls),
]
