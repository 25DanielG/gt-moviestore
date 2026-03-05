from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='popularity_map.index'),
    path('api/regions/', views.api_regions, name='popularity_map.api_regions'),
]