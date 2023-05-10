"""blog_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .views import PostListView,PostDetailView,PostCreateView,PostUpdateView,PostDeleteView,UserPostListView

app_name = 'blog'

from .import views

urlpatterns = [
    path('',PostListView.as_view() ,name = 'blog_home'),
    path('about/',views.about, name = 'blog_about'),
    path('post/<int:pk>/',views.postdetail,name = 'post_detail'),
    path('post/new/',PostCreateView.as_view() ,name = 'post_create'),
    path('post/<int:pk>/update/',PostUpdateView.as_view() ,name = 'post_update'),
    path('post/<int:pk>/delete/',PostDeleteView.as_view() ,name = 'post_delete'),
    path('user/<str:username>',UserPostListView.as_view() ,name = 'user_posts'),
    path('post/<int:pk>/comment/',views.post_comment ,name = 'user_comment'),
]

