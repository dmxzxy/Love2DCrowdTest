from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^project/create/$', views.project_create, name='project_create'),
    url(r'^project/(?P<project_id>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^project/help/(?P<project_id>[0-9]+)/$', views.project_help, name='project_help'),
    
    url(r'^protocal/$', views.index, name='protocal_detail_parent'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
    url(r'^protocal/create/(?P<module_id>[0-9]+)$', views.protocal_create, name='protocal_create'),
    url(r'^protocal/edit/(?P<protocal_id>[0-9]+)$', views.protocal_edit, name='protocal_edit'),
    url(r'^protocal/delete/$', views.protocal_delete, name='protocal_delete'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
]