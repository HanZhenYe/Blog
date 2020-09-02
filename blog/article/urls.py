from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_index),
    path('article/', views.articles),
    path('article/page/', views.article_page),
]
