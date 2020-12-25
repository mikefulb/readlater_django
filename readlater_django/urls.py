from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('readlater/', include('readlater.urls')),
    path('admin/', admin.site.urls),
]
