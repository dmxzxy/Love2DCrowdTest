from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^project/create/$', views.project_create, name='project_create'),
    url(r'^project/(?P<project_id>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^project/help/(?P<project_id>[0-9]+)/$', views.project_help, name='project_help'),
    url(r'^project/export/(?P<project_id>[0-9]+)/$', views.project_export, name='project_export'),
    url(r'^project/download/(?P<project_id>[0-9]+)/$', views.project_download, name='project_download'),
    
    url(r'^protocal/$', views.index, name='protocal_detail_parent'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
    url(r'^protocal/create/(?P<module_id>[0-9]+)$', views.protocal_create, name='protocal_create'),
    url(r'^protocal/edit/(?P<protocal_id>[0-9]+)$', views.protocal_edit, name='protocal_edit'),
    url(r'^protocal/delete/$', views.protocal_delete, name='protocal_delete'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
    
    url(r'^segments/(?P<protocal_id>[0-9]+)$', views.segments_detail, name='segments_detail'),
    url(r'^segment/create/$', views.index, name='segment_create_parent'),
    url(r'^segment/create/(?P<protocal_id>[0-9]+)$', views.segment_create, name='segment_create'),
    url(r'^segment/edit/$', views.index, name='segment_edit_parent'),
    url(r'^segment/edit/(?P<segment_id>[0-9]+)$', views.segment_edit, name='segment_edit'),
    url(r'^segment/delete/$', views.segment_delete, name='segment_delete'),
    
    url(r'^module/create/(?P<project_id>[0-9]+)$', views.module_create, name='module_create'),
    url(r'^module/detail/(?P<module_id>[0-9]+)$', views.module_detail, name='module_detail'),
]