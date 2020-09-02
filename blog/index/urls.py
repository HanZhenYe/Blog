from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('search/', views.search),
    path('login/', views.login),
    path('quit/', views.quit),
    path('tool/', views.tool)
]

