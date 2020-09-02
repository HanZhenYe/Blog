from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('favicon.ico',RedirectView.as_view(url='static/img/favicon.ico')),
    path('', include('index.urls')),
    path('article/', include('article.urls')),
    path('note/', include('note.urls')),
    path('book/', include('book.urls')),
    path('admin/', admin.site.urls),
]
