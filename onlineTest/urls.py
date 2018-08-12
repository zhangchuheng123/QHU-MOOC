"""onlineTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from backend import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^examlist/', views.examlist, name='examlist'),
    url(r'^exam/', views.exam, name='exam'),
    url(r'^exam/(?P<id>\w{0,50})/', views.exam, name='exam'),
    url(r'^changepassword/', views.changepassword, name='changepassword'),
    url(r'^showall/', views.showall, name='showall'),
    url(r'^showall/(?P<id>\w{0,50})/', views.exam, name='showall'),
    url(r'^downloadscores/', views.downloadscores, name='downloadscores'),
    url(r'^downloadscores/(?P<id>\w{0,50})/', views.exam, name='downloadscores'),
    url(r'^$', views.index, name='index'),
]