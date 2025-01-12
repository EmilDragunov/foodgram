"""Главный файл URL-ов проекта."""
from django.contrib import admin
from django.urls import path, include
from api.recipes.views import short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:link>/', short_link, name='short-link'),
]
