from django.contrib import admin
from django.urls import path, include
from . import views
app_name ='accounts'
urlpatterns = [
    path('', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('update', views.update, name='update'),
    path('', include('cal.urls')),
    path('forum/', include('blog.urls')),
    # path('signout', views.signout, name='signout'),
    path('logout', views.logout, name='logout'),
    path('homepage/manager', views.m_homepage, name='M_homepage'),
    path('homepage/employee', views.e_homepage, name='E_homepage'),
    path('addevent',views.eventdata, name = 'addevent'),
]
