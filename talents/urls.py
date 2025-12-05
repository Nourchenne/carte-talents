# talents/urls.py
from django.urls import path
from . import views

app_name = 'talents'

urlpatterns = [
    path('', views.talent_list, name='talent_list'),
    path('collaborateurs/', views.collaborateur_list, name='collaborateur_list'),
]