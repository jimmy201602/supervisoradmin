"""superadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from superadmin.views import getlogtail,showMain,showNode,getlist,showGroup,json_restart,json_start,json_stop,readlog

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^activitylog/', getlogtail.as_view(),name='activitylog'),    
    url(r'^$', showMain.as_view(),name='index'),    
    url(r'^node/(?P<node_name>\w+)/$', showNode.as_view(),name='show_node'), 
    url(r'^node/name/list/$',getlist.as_view(),name='node_list'),
    url(r'^group/(?P<group_name>\w+)/environment/(?P<environment_name>\w+)/$',showGroup.as_view(),name='show_group'),
    url(r'^node/(?P<node_name>\w+)/process/(?P<process_name>\w+)/restart/$',json_restart.as_view(),name='json_restart'),
    url(r'^node/(?P<node_name>\w+)/process/(?P<process_name>\w+)/start/$',json_start.as_view(),name='json_start'),
    url(r'^node/(?P<node_name>\w+)/process/(?P<process_name>\w+)/stop/$',json_stop.as_view(),name='json_stop'),
    url(r'^node/(?P<node_name>\w+)/process/(?P<process_name>\w+:\w+)/readlog/$',readlog.as_view(),name='readlog'),
]
