from django.shortcuts import render

# Create your views here.
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_story, name='generate_story'),
]
