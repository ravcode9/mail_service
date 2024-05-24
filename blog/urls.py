from django.urls import path
from django.views.decorators.cache import cache_page

from blog.views import BlogDetailView

urlpatterns = [
    path('<int:pk>/', cache_page(60)(BlogDetailView.as_view()), name='blog_detail'),
]
