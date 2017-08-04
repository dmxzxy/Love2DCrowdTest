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
    url(r'^project/downloadproto/(?P<project_id>[0-9]+)/$', views.project_download_proto, name='project_download_proto'),
    url(r'^project/downloadcpp/(?P<project_id>[0-9]+)/$', views.project_download_cpp, name='project_download_cpp'),
    
    url(r'^module/create/(?P<project_id>[0-9]+)$', views.module_create, name='module_create'),
    url(r'^module/detail/(?P<module_id>[0-9]+)$', views.module_detail, name='module_detail'),

    url(r'^protocal/$', views.index, name='protocal_detail_parent'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
    url(r'^protocal/create/(?P<project_id>[0-9]+)/(?P<module_id>[0-9]+)$', views.protocal_create, name='protocal_create'),
    url(r'^protocal/edit/(?P<project_id>[0-9]+)/(?P<protocal_id>[0-9]+)$', views.protocal_edit, name='protocal_edit'),
    url(r'^protocal/delete/$', views.protocal_delete, name='protocal_delete'),
    url(r'^protocal/(?P<protocal_id>[0-9]+)$', views.protocal_detail, name='protocal_detail'),
    
    url(r'^segments/(?P<protocal_id>[0-9]+)$', views.segments_detail, name='segments_detail'),
    url(r'^segment/create/$', views.index, name='segment_create_parent'),
    url(r'^segment/create/(?P<protocal_id>[0-9]+)$', views.segment_create, name='segment_create'),
    url(r'^segment/edit/$', views.index, name='segment_edit_parent'),
    url(r'^segment/edit/(?P<segment_id>[0-9]+)$', views.segment_edit, name='segment_edit'),
    url(r'^segment/delete/$', views.segment_delete, name='segment_delete'),

    url(r'^enum/$', views.index, name='enum_detail_parent'),
    url(r'^enum/(?P<enum_id>[0-9]+)$', views.enum_detail, name='enum_detail'),
    url(r'^enum/create/(?P<module_id>[0-9]+)$', views.enum_create, name='enum_create'),
    url(r'^enum/edit/(?P<enum_id>[0-9]+)$', views.enum_edit, name='enum_edit'),
    url(r'^enum/delete/$', views.enum_delete, name='enum_delete'),

    url(r'^enumsegments/(?P<enum_id>[0-9]+)$', views.enum_segments_detail, name='enum_segments_detail'),
    url(r'^enumsegments/create/$', views.index, name='enum_segment_create_parent'),
    url(r'^enumsegments/create/(?P<enum_id>[0-9]+)$', views.enum_segment_create, name='enum_segment_create'),
    url(r'^enumsegments/edit/$', views.index, name='enum_segment_edit_parent'),
    url(r'^enumsegments/edit/(?P<segment_id>[0-9]+)$', views.enum_segment_edit, name='enum_segment_edit'),
    url(r'^enumsegments/delete/$', views.enum_segment_delete, name='enum_segment_delete'),

    url(r'^customtype/$', views.index, name='customtype_detail_parent'),
    url(r'^customtype/(?P<customtype_id>[0-9]+)$', views.customtype_detail, name='customtype_detail'),
    url(r'^customtype/create/$', views.index, name='customtype_create_parent'),
    url(r'^customtype/create/(?P<module_id>[0-9]+)$', views.customtype_create, name='customtype_create'),
    url(r'^customtype/delete/$', views.customtype_delete, name='customtype_delete'),
    url(r'^customtype/edit/$', views.index, name='customtype_edit_parent'),
    url(r'^customtype/edit/(?P<customtype_id>[0-9]+)$', views.customtype_edit, name='customtype_edit'),

    url(r'^customtype_detail_by_segment/$', views.index, name='customtype_detail_by_segment_parent'),
    url(r'^customtype_detail_by_segment/(?P<segment_type_id>[0-9]+)/$', views.customtype_detail_by_segment, name='customtype_detail_by_segment'),
    url(r'^enum_detail_by_segment/$', views.index, name='enum_detail_by_segment_parent'),
    url(r'^enum_detail_by_segment/(?P<segment_type_id>[0-9]+)/$', views.enum_detail_by_segment, name='enum_detail_by_segment'),

    url(r'^customtypesegments/(?P<customtype_id>[0-9]+)$', views.customtype_segments_detail, name='customtype_segments_detail'),
    url(r'^customtypesegments/create/$', views.index, name='customtype_segment_create_parent'),
    url(r'^customtypesegments/create/(?P<customtype_id>[0-9]+)$', views.customtype_segment_create, name='customtype_segment_create'),
    url(r'^customtypesegments/edit/$', views.index, name='customtype_segment_edit_parent'),
    url(r'^customtypesegments/edit/(?P<segment_id>[0-9]+)$', views.customtype_segment_edit, name='customtype_segment_edit'),
    url(r'^customtypesegments/delete/$', views.customtype_segment_delete, name='customtype_segment_delete'),
]