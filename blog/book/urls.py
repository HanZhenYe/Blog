from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('book/', views.book_details),
    path('catalog/', views.book_catalog)
]
