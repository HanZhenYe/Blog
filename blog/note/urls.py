from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_index),
    path('note/', views.note_details),
    path('note/catalog/', views.note_catalog),
]
