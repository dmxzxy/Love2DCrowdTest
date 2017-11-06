# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import os

# Create your views here.
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.http.response import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext  

from datetime import datetime
from string import strip

from protocal.models import *
from protocal import export_utils, utils, sync_proto, export_config
from protocal.utils import try_parse_int

cur_edit_project = None

def get_module_by_id(module_id):
    global cur_edit_project;
    if cur_edit_project == None:
        return None

    cur_module = None
    if try_parse_int(module_id) == 0:
        cur_module = Module(
            id = 0,
            name = 'global',
            namedesc = '全局模块',
            desc = '',
            project = cur_edit_project,
            namespace = cur_edit_project.namespace)
    else:
        cur_module = get_object_or_404(Module, pk=module_id)
    return cur_module

def try_get_module(model):
    global cur_edit_project;
    if cur_edit_project == None:
        return None

    try:
        cur_module = model.Module;
    except:
        cur_module = Module(
            id = 0,
            name = 'global',
            namedesc = '全局模块',
            desc = '',
            project = cur_edit_project,
            namespace = cur_edit_project.namespace)
    return cur_module


def project_help(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    protocals = Protocal.objects.filter(module__in = modules).order_by('-timestamp')
    protocal_types = ProtocalType.objects.all()    
    return render(request, 'project_help.html', { 'cur_project':cur_project,
                                                  'modules':modules,
                                                  'protocals':protocals,
                                                  'protocal_types':protocal_types,
                                                  })

def index(request):
	projects = Project.objects.all().order_by('-timestamp')
	return render(request, 'index.html',{'projects' : projects})


# project -----------------------------------------------------
def project_create(request):
	if request.method == 'POST': 
		project_name = request.POST['project_name'] 
		project_namespace = request.POST['project_namespace'] 

		print 'project_name:' + project_name
		print 'project_namespace:' + project_namespace

		if project_name and project_namespace:
			project = Project(title = strip(project_name),namespace = strip(project_namespace))
			project.save()
		else:
			raise ValidationError("name or namespace should not be null.");

		return HttpResponse("<h1>Created successfully .</h1>")  
	else:
		return HttpResponse("<h1>Invalid request.</h1>")  



def project_detail(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)

    global cur_edit_project;
    cur_edit_project = cur_project

    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    global_module = Module(
        id = 0,
        name = 'global',
        namedesc = '全局模块',
        desc = '',
        project = cur_edit_project,
        namespace = cur_edit_project.namespace)

    _modules = [];
    for m in modules:
        _modules.append(m);
    _modules.append(global_module)

    protocals = Protocal.objects.filter(Q(module__in = _modules)).order_by('-timestamp')
    enums = Enum.objects.filter(Q(module__in = _modules)).order_by('-timestamp')
    customtypes = CustomType.objects.filter(Q(module__in = _modules)).order_by('-timestamp')
    protocal_types = ProtocalType.objects.all()
    protocals = protocals.order_by('protocal_id')
    return render(request, 'project_detail.html', { 'cur_project':cur_project,
    												'modules':modules,
    												'protocals':protocals,
    												'protocal_types':protocal_types,
                                                    'enums':enums,
                                                    'customtypes':customtypes,
													})

def project_sync_proto(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST': 

        cur_project.is_exporting = True
        cur_project.save(update_fields=['is_exporting'])

        sugget_version = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        project_export = ProjectExport(project = cur_project,
                                       version = sugget_version,
                                       status = 1,
                                       )
        project_export.save()

        try:
            sync_proto.doSync(cur_project)
            project_export.status = 2
            project_export.save(update_fields=['status'])
        except Exception,e:
            project_export.status = 3
            project_export.save(update_fields=['status'])
            utils.print_trace()
            raise e
        finally:
            cur_project.is_exporting = False
            cur_project.save(update_fields=['is_exporting'])

        return HttpResponse("<h1>Export successfully .</h1>")  
    else:
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocals = Protocal.objects.filter(module__in = modules).order_by('-timestamp')
        protocal_types = ProtocalType.objects.all()
        need_update = sync_proto.testUpdate(cur_project)
        exported_projects = ProjectExport.objects.filter(project = cur_project).order_by('-timestamp')[:10]
        return render(request, 'project_sync_proto.html',{'cur_project':cur_project,
                                                          'modules':modules,
                                                          'protocals':protocals,
                                                          'protocal_types':protocal_types,
                                                          'exported_projects':exported_projects,
                                                          'need_update':need_update,
                                                      })
    


def project_force_sync_proto(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST': 

        cur_project.is_exporting = True
        cur_project.save(update_fields=['is_exporting'])

        sugget_version = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        project_export = ProjectExport(project = cur_project,
                                       version = sugget_version,
                                       status = 1,
                                       )
        project_export.save()

        try:
            sync_proto.doForceSync(cur_project)
            project_export.status = 2
            project_export.save(update_fields=['status'])
        except Exception,e:
            project_export.status = 3
            project_export.save(update_fields=['status'])
            utils.print_trace()
            raise e
        finally:
            cur_project.is_exporting = False
            cur_project.save(update_fields=['is_exporting'])

        return HttpResponse("<h1>Export successfully .</h1>")  
    else:
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocals = Protocal.objects.filter(module__in = modules).order_by('-timestamp')
        protocal_types = ProtocalType.objects.all()
        need_update = sync_proto.testUpdate(cur_project)
        exported_projects = ProjectExport.objects.filter(project = cur_project).order_by('-timestamp')[:10]
        return render(request, 'project_sync_proto.html',{'cur_project':cur_project,
                                                          'modules':modules,
                                                          'protocals':protocals,
                                                          'protocal_types':protocal_types,
                                                          'exported_projects':exported_projects,
                                                          'need_update':need_update,
                                                      })

    
def project_export(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST': 
        
        export_version = request.POST['export_version'] 
        export_force = (request.POST['export_force']  == 'true' )
        export_clean = (request.POST['export_clean']  == 'true' )
        
        print 'export_force:' + str(export_force)
        print 'export_clean:' + str(export_clean)
        
        if cur_project.is_exporting and not export_force:
            raise Exception('Project is exporting.Wait until exporting done or toggel option [EXPORT FORCE]')
        
        project_export = ProjectExport(project = cur_project,
                                       version = export_version,
                                       status = 1,
                                       )
        project_export.save()
        
        cur_project.is_exporting = True
        cur_project.save(update_fields=['is_exporting'])
        
        export_setting = ExporterSetting.objects.first()
        try:
            export_setting.export_clean = export_clean
            export_utils.do_export(cur_project, export_version,export_setting)
            project_export.status = 2
            project_export.save(update_fields=['status'])
        except Exception,e:
            project_export.status = 3
            project_export.save(update_fields=['status'])
            utils.print_trace()
            raise e
        finally:
            cur_project.is_exporting = False
            cur_project.save(update_fields=['is_exporting'])
        
        return HttpResponse("<h1>Export successfully .</h1>")  
    else:
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocals = Protocal.objects.filter(module__in = modules).order_by('-timestamp')
        protocal_types = ProtocalType.objects.all()
    
        exported_projects = ProjectExport.objects.filter(project = cur_project).order_by('-timestamp')[:10]
        sugget_version = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        return render(request, 'project_export.html',{'cur_project':cur_project,
                                                      'modules':modules,
                                                      'protocals':protocals,
                                                      'protocal_types':protocal_types,
                                                      'exported_projects':exported_projects,
                                                      'sugget_version':sugget_version,
                                                  })

def project_download(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    export_setting = ExporterSetting.objects.first()
    def file_iterator(file_path, chunk_size=512):
        with open(file_path,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = 'protocal_lua.zip'                
    the_file_path = export_setting.export_path + '/protocal'+  '/archive/' + the_file_name
#     print 'the_file_path:' + the_file_path
    file_size = os.path.getsize(the_file_path)
    print 'file size:' + str(file_size)
    response = StreamingHttpResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    response['Content-Length'] = file_size
    return response

def project_download_proto(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    export_setting = ExporterSetting.objects.first()
    def file_iterator(file_path, chunk_size=512):
        with open(file_path,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = 'protocal_proto.zip'                
    the_file_path = export_setting.export_path + '/protocal'+  '/archive/' + the_file_name
#     print 'the_file_path:' + the_file_path
    file_size = os.path.getsize(the_file_path)
    print 'file size:' + str(file_size)
    response = StreamingHttpResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    response['Content-Length'] = file_size
    return response
    

def project_download_cpp(request,project_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    export_setting = ExporterSetting.objects.first()
    def file_iterator(file_path, chunk_size=512):
        with open(file_path,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = 'protocal_cpp.zip'                
    the_file_path = export_setting.export_path + '/protocal'+  '/archive/' + the_file_name
#     print 'the_file_path:' + the_file_path
    file_size = os.path.getsize(the_file_path)
    print 'file size:' + str(file_size)
    response = StreamingHttpResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    response['Content-Length'] = file_size
    return response

# enum ------------------------------------------------------------
def enum_detail(request,enum_id):
    cur_enum = get_object_or_404(Enum, pk=enum_id)
    segments = EnmuSegment.objects.filter(belong = cur_enum)
    return render(request, 'enum_detail_dialog.html',{
                                                  'cur_enum':cur_enum,
                                                  'segments':segments,
                                                  }) 

def enum_create(request,module_id,enum_id = 0):
    if request.method == 'POST': 
        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_project = cur_module.project
        cur_enum = Enum.objects.filter(pk=enum_id).first()

        enum_name = request.POST['enum_name']
        enum_desc = request.POST['enum_desc']
        enum_inner_type = request.POST['enum_inner_type']
        enum_inner_protocal_id = request.POST['enum_inner_protocal_id'] 
        enum_namespace = cur_module.namespace + "." + enum_name

        if not enum_name or strip(enum_name) == '':
            raise ValidationError("enum_name should not be null.");
        if not enum_desc:
            raise ValidationError("enum_desc should not be null.");
        else:
            inner_protocal = None
            inner_customtype = None
            if try_parse_int(enum_inner_type) == 0:
                if (not enum_inner_protocal_id) or (try_parse_int(enum_inner_protocal_id) == 0):
                    inner_protocal = None
                else:
                    inner_protocal = get_object_or_404(Protocal, pk=enum_inner_protocal_id) 
                    enum_namespace = inner_protocal.namespace + '.' + enum_name

            if try_parse_int(enum_inner_type) == 2:
                if (not enum_inner_protocal_id) or (try_parse_int(enum_inner_protocal_id) == 0):
                    inner_customtype = None
                else:
                    inner_customtype = get_object_or_404(CustomType, pk=enum_inner_protocal_id) 
                    enum_namespace = inner_customtype.namespace + '.' + enum_name

            if cur_enum:   
                Enum.objects.filter(pk=enum_id).update(name = strip(enum_name),
                                                        desc = enum_desc,
                                                        module = cur_module,
                                                        namespace = enum_namespace,
                                                        belong = inner_protocal,
                                                        belong_ct = inner_customtype,
                                                        )


                segment_type = SegmentType.objects.filter(id = cur_enum.type.id)
                if segment_type:
                    segment_type.update(name = strip(enum_namespace),desc = enum_desc)
            else:
                enum = Enum(name = strip(enum_name),
                            desc = enum_desc,
                            module = cur_module,
                            namespace = enum_namespace,
                            belong = inner_protocal,
                            belong_ct = inner_customtype,
                            )
                enum.save()

                segment_type = SegmentType(name = strip(enum_namespace),
                                           desc = enum_desc,
                                           module = cur_module,
                                           protocal = inner_protocal,
                                           is_basic = False,
                                           project = cur_project,
                                           provider_type = 1,
                                           )
                segment_type.save()
                Enum.objects.filter(id=enum.id).update(type = segment_type)

        return HttpResponse("<h1>Created Enum successfully .</h1>")  
    else:
        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_project = cur_module.project
        cur_enum = Enum.objects.filter(pk=enum_id).first()
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocals = Protocal.objects.filter(Q(module = cur_module))
        customtypes = CustomType.objects.filter(Q(module = cur_module)).order_by('-timestamp')

        return render(request, 'enum_new.html',{  'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'cur_enum':cur_enum,
                                                  'modules':modules,
                                                  'protocals':protocals, 
                                                  'customtypes':customtypes,                                              
                                                  }) 

def enum_edit(request,enum_id):
    cur_enum = get_object_or_404(Enum, pk=enum_id)
    cur_module = try_get_module(cur_enum)
    if cur_module == None:
        return index(request)
    return enum_create(request,cur_module.id,cur_enum.id)

def enum_delete(request):
    if request.method == 'POST': 
        enum_id = request.POST['enum_id'] 
        cur_enum = get_object_or_404(Enum, pk=enum_id)
        cur_enum_type = get_object_or_404(SegmentType, pk=cur_enum.type.id)

        if cur_enum:
            cur_enum.delete()
            cur_enum_type.delete()
        else:
            raise ValidationError("enum_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  

def enum_detail_by_segment(request,segment_type_id):
    cur_segment_type = get_object_or_404(SegmentType, pk=segment_type_id)
    cur_enum = get_object_or_404(Enum, type=cur_segment_type)
    segments = EnmuSegment.objects.filter(belong = cur_enum)
    return render(request, 'enum_detail_dialog.html',{
                                                  'cur_enum':cur_enum,
                                                  'segments':segments,
                                                  }) 
# enum segments ------------------------------------------------------------------------------------
def enum_segments_detail(request,enum_id):
    cur_enum = get_object_or_404(Enum, pk=enum_id)
    cur_module = try_get_module(cur_enum)
    if cur_module == None:
        return index(request)
    cur_project = cur_module.project
    
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    enumsegments = EnmuSegment.objects.filter(belong = cur_enum).order_by('value')
    
    return render(request, 'enum_segments_detail.html',{  'cur_project':cur_project,
                                                          'cur_module':cur_module,
                                                          'cur_enum':cur_enum,
                                                          'modules':modules,
                                                          'enumsegments':enumsegments,
                                                        })

def enum_segment_create(request,enum_id,segment_id = 0):
    if request.method == 'POST': 
        cur_enum = get_object_or_404(Enum, pk=enum_id)
        cur_segment = EnmuSegment.objects.filter(pk=segment_id)
        cur_module = try_get_module(cur_enum)
        if cur_module == None:
            return index(request)
        cur_project = cur_module.project
        
        segment_name = request.POST['segment_name']
        segment_value = request.POST['segment_value']  
        segment_desc = request.POST['segment_desc'] 
        segment_namespace = cur_enum.namespace + '.' + segment_name
        
        if not segment_name:
            raise ValidationError("segment_name should not be null.");
        if not segment_desc:
            raise ValidationError("segment_desc should not be null.");
        if not segment_value :
            raise ValidationError("segment_value should not be null.");
        else:
            if cur_segment:
                cur_segment.update( name = strip(segment_name),
                                    namespace = segment_namespace,
                                    value = segment_value,
                                    desc = segment_desc,
                                    belong = cur_enum,
                                    )
            else:
                segment = EnmuSegment(  name = strip(segment_name),
                                        namespace = segment_namespace,
                                        value = segment_value,
                                        desc = segment_desc,
                                        belong = cur_enum,
                                        )
        
                segment.save()
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        cur_enum = get_object_or_404(Enum, pk=enum_id)
        cur_segment = EnmuSegment.objects.filter(id=segment_id).first()
        cur_module = try_get_module(cur_enum)
        if cur_module == None:
            return index(request)
        cur_project = cur_module.project
        
        return render(request, 'enum_segment_create_dialog.html',{
                                                  'cur_enum':cur_enum,
                                                  'cur_segment':cur_segment, 
                                                  'cur_module':cur_module,
                                                  'cur_project':cur_project
                                                  }) 

def enum_segment_edit(request,segment_id):
    cur_segment = get_object_or_404(EnmuSegment, pk=segment_id)
    return enum_segment_create(request,cur_segment.belong.id,cur_segment.id)

def enum_segment_delete(request):
    if request.method == 'POST': 
        segment_id = request.POST['segment_id'] 
        cur_segment = get_object_or_404(EnmuSegment, pk=segment_id)

        if cur_segment:
            cur_segment.delete()

        else:
            raise ValidationError("segment_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  

# customType ------------------------------------------------------------
def customtype_detail(request,customtype_id = 0):
    cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
    segments = CustomTypeSegment.objects.filter(belong = cur_customtype)
    return render(request, 'custom_type_detail_dialog.html',{
                                                  'cur_customtype':cur_customtype,
                                                  'segments':segments,
                                                  }) 

def customtype_create(request,module_id,customtype_id = 0):
    if request.method == 'POST': 
        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_project = cur_module.project
        cur_customtype = CustomType.objects.filter(pk=customtype_id).first()

        customtype_name = request.POST['customtype_name']
        customtype_desc = request.POST['customtype_desc']
        customtype_inner_type = request.POST['customtype_inner_type']
        customtype_inner_protocal_id = request.POST['customtype_inner_protocal_id'] 
        customtype_namespace = cur_module.namespace + "." + customtype_name

        if not customtype_name or strip(customtype_name) == '':
            raise ValidationError("customtype_name should not be null.");
        if not customtype_desc:
            raise ValidationError("customtype_desc should not be null.");
        else:
            inner_protocal = None
            inner_customtype = None
            if try_parse_int(customtype_inner_type) == 0:
                if (not customtype_inner_protocal_id) or (try_parse_int(customtype_inner_protocal_id) == 0):
                    inner_protocal = None
                else:
                    inner_protocal = get_object_or_404(Protocal, pk=customtype_inner_protocal_id) 
                    customtype_namespace = inner_protocal.namespace + '.' + customtype_name

            if try_parse_int(customtype_inner_type) == 2:
                if (not customtype_inner_protocal_id) or (try_parse_int(customtype_inner_protocal_id) == 0):
                    inner_customtype = None
                else:
                    inner_customtype = get_object_or_404(CustomType, pk=customtype_inner_protocal_id) 
                    customtype_namespace = inner_customtype.namespace + '.' + customtype_name


            if cur_customtype:          
                CustomType.objects.filter(pk=customtype_id).update(name = strip(customtype_name),
                                                                    desc = customtype_desc,
                                                                    module = cur_module,
                                                                    namespace = customtype_namespace,
                                                                    belong = inner_protocal,
                                                                    belong_ct = inner_customtype,
                                                                    )

                segment_type = SegmentType.objects.filter(id = cur_enum.type.id)
                if segment_type:
                    segment_type.update(name = strip(customtype_namespace),desc = customtype_desc)
            else:
                customtype = CustomType(name = strip(customtype_name),
                            desc = customtype_desc,
                            module = cur_module,
                            namespace = customtype_namespace,
                            belong = inner_protocal,
                            belong_ct = inner_customtype,
                            )
    
                customtype.save()

                segment_type = SegmentType(name = strip(customtype_namespace),
                                           desc = customtype_desc,
                                           module = cur_module,
                                           protocal = inner_protocal,
                                           is_basic = False,
                                           project = cur_project,
                                           provider_type = 2,
                                           )
                segment_type.save()
                CustomType.objects.filter(id=customtype.id).update(type = segment_type)

        return HttpResponse("<h1>Created CustomType successfully .</h1>")  
    else:
        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_project = cur_module.project
        cur_customtype = CustomType.objects.filter(pk=customtype_id).first()
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocals = Protocal.objects.filter(Q(module = cur_module)).order_by('-timestamp')
        customtypes = CustomType.objects.filter(Q(module = cur_module)).order_by('-timestamp')
        if cur_customtype:
            customtypes = customtypes.exclude(pk=cur_customtype.id)

        return render(request, 'custom_type_create_dialog.html',{  'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'cur_customtype':cur_customtype,
                                                  'modules':modules,
                                                  'protocals':protocals,
                                                  'customtypes':customtypes,                                               
                                                  }) 

def customtype_edit(request,customtype_id):
    cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
    cur_module = try_get_module(cur_customtype)
    if cur_module == None:
        return index(request)
    return customtype_create(request,cur_module.id,cur_customtype.id)

def customtype_delete(request):
    if request.method == 'POST': 
        customtype_id = request.POST['customtype_id'] 
        cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
        cur_customtype_type = get_object_or_404(SegmentType, pk=cur_customtype.type.id)

        if cur_customtype:
            cur_customtype.delete()
            cur_customtype_type.delete()

        else:
            raise ValidationError("customtype_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  

def customtype_detail_by_segment(request,segment_type_id):
    cur_segment_type = get_object_or_404(SegmentType, pk=segment_type_id)
    cur_customtype = get_object_or_404(CustomType, type=cur_segment_type)
    segments = CustomTypeSegment.objects.filter(belong = cur_customtype)
    return render(request, 'custom_type_detail_dialog.html',{
                                                  'cur_customtype':cur_customtype,
                                                  'segments':segments,
                                                  }) 

# customtype segments ------------------------------------------------------------------------------------
def customtype_segments_detail(request,customtype_id):
    cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
    cur_module = try_get_module(cur_customtype)
    if cur_module == None:
        return index(request)
    cur_project = cur_module.project
    
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    segments = CustomTypeSegment.objects.filter(belong = cur_customtype).order_by('timestamp')
    
    return render(request, 'custom_type_segments_detail.html',{  'cur_project':cur_project,
                                                          'cur_module':cur_module,
                                                          'cur_customtype':cur_customtype,
                                                          'modules':modules,
                                                          'segments':segments,
                                                        })

def customtype_segment_create(request,customtype_id,segment_id = 0):
    if request.method == 'POST': 
        cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
        cur_customtype_segment = CustomTypeSegment.objects.filter(pk=segment_id)
        cur_module = try_get_module(cur_customtype)
        if cur_module == None:
            return index(request)
        cur_project = cur_module.project
        
        customtype_segment_name = request.POST['segment_name'] 
        customtype_segment_desc = request.POST['segment_desc'] 
        customtype_segment_type_id = request.POST['segment_type_id'] 
        segment_extra_type1_id = request.POST['segment_extra_type1_id'] 
        segment_extra_type2_id = request.POST['segment_extra_type2_id'] 
        customtype_segment_protocal_type_id = request.POST['segment_protocal_type_id'] 
        segment_default_value = request.POST['segment_default_value']
        customtype_segment_namespace = cur_customtype.namespace + '.' + customtype_segment_name
        
        if not customtype_segment_name:
            raise ValidationError("custom_type_segment_name should not be null.");
        if not customtype_segment_desc:
            raise ValidationError("custom_type_segment_desc should not be null.");
        if not customtype_segment_protocal_type_id :
            raise ValidationError("custom_type_segment_protocal_type_id should not be null.");
        if not customtype_segment_type_id:
            raise ValidationError("custom_type_segment_type should not be null.");
        else:
            customtype_segment_type = get_object_or_404(SegmentType, pk=customtype_segment_type_id) 
            segment_extra_type1 = get_object_or_404(SegmentType, pk=segment_extra_type1_id) 
            segment_extra_type2 = get_object_or_404(SegmentType, pk=segment_extra_type2_id) 
            customtype_segment_protocal_type = get_object_or_404(SegmentProtoType, pk=customtype_segment_protocal_type_id) 
            if try_parse_int(segment_default_value):
                enumsegemet = get_object_or_404(EnmuSegment, pk=segment_default_value)
            else:
                enumsegemet = None
            
            if cur_customtype_segment:
                cur_customtype_segment.update(name = strip(customtype_segment_name),
                                    namespace = customtype_segment_namespace,
                                    desc = customtype_segment_desc,
                                    belong = cur_customtype,
                                    protocal_type = customtype_segment_protocal_type,
                                    type = customtype_segment_type,
                                    defaultEnum = enumsegemet
                                    )
            else:
                customtype_segment = CustomTypeSegment(name = strip(customtype_segment_name),
                                    namespace = customtype_segment_namespace,
                                    desc = customtype_segment_desc,
                                    belong = cur_customtype,
                                    protocal_type = customtype_segment_protocal_type,
                                    type = customtype_segment_type,
                                    defaultEnum = enumsegemet
                                    )
    
                customtype_segment.save()

        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        cur_customtype = get_object_or_404(CustomType, pk=customtype_id)
        cur_protocal = cur_customtype.belong
        cur_segment = CustomTypeSegment.objects.filter(id=segment_id).first()
        cur_module = try_get_module(cur_customtype)
        if cur_module == None:
            return index(request)
        cur_project = cur_module.project
        segment_proto_types = SegmentProtoType.objects.all()
        segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(module=cur_module))).order_by('-is_basic','-show_priority','-timestamp')
        if cur_protocal:
            segment_types = segment_types.exclude(~Q(protocal = None), ~Q(protocal = cur_protocal))
        else:
            segment_types = segment_types.exclude(~Q(protocal = None))

        segment_types = segment_types.exclude(Q(pk=cur_customtype.type.id))

        for segment_type in segment_types:
            if segment_type.provider_type == 1:
                enum = Enum.objects.filter(type = segment_type)
                enumsegments = EnmuSegment.objects.filter(belong = enum)
                segment_type.enumsegments = enumsegments

        return render(request, 'custom_type_segment_create_dialog.html',{
                                                  'cur_customtype':cur_customtype,
                                                  'cur_segment':cur_segment, 
                                                  'cur_module':cur_module,
                                                  'cur_project':cur_project,
                                                  'segment_proto_types':segment_proto_types,
                                                  'segment_types':segment_types,
                                                  }) 

def customtype_segment_edit(request,segment_id):
    cur_segment = get_object_or_404(CustomTypeSegment, pk=segment_id)
    return customtype_segment_create(request,cur_segment.belong.id,cur_segment.id)

def customtype_segment_delete(request):
    if request.method == 'POST': 
        segment_id = request.POST['custom_type_segment_id'] 
        cur_segment = get_object_or_404(CustomTypeSegment, pk=segment_id)

        if cur_segment:
            cur_segment.delete()

        else:
            raise ValidationError("segment_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  

# protocal --------------------------------------------------------
def protocal_detail(request,protocal_id):
    cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
    innerEnums = Enum.objects.filter(belong = cur_protocal)
    innerCustomTypes = CustomType.objects.filter(belong = cur_protocal)
    if len(innerEnums) > 0:
        cur_protocal.innerEnums = innerEnums;
    if len(innerCustomTypes) > 0:
        cur_protocal.innerCustomTypes = innerCustomTypes;
    segments = Segment.objects.filter(protocal = cur_protocal)
    return render(request, 'protocal_detail_dialog.html',{
                                                  'cur_protocal':cur_protocal,
                                                  'segments':segments,
                                                  }) 

def protocal_create(request,project_id,module_id,protocal_id = 0):
    if request.method == 'POST': 
        cur_project = get_object_or_404(Project, pk=project_id)

        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_protocal = Protocal.objects.filter(pk=protocal_id).first()
        
        protocal_name = request.POST['protocal_name'] 
        protocal_desc = request.POST['protocal_desc'] 
        protocal_protocal_id = request.POST['protocal_id'] 
        protocal_protocal_unique_id = try_parse_int(protocal_protocal_id)
        protocal_type_id = request.POST['protocal_type_id'] 
        protocal_relate_protocal_id = request.POST['protocal_relate_protocal_id'] 
        protocal_namespace = cur_project.namespace + "." + protocal_name
        if cur_module:
            protocal_namespace = cur_module.namespace + "." + protocal_name
        
        if not protocal_name or strip(protocal_name) == '':
            raise ValidationError("protocal_name should not be null.");
        if not protocal_desc:
            raise ValidationError("protocal_desc should not be null.");
        if not protocal_protocal_id :
            raise ValidationError("protocal_protocal_id should not be null.");
        if not protocal_protocal_unique_id :
            raise ValidationError("protocal_protocal_id should be int.");
        if not protocal_type_id:
            raise ValidationError("protocal_type should not be null.");
        else:
            protocal_protocal_unique_id = cur_project.id + protocal_protocal_unique_id
            
            protocal_relate_protocal = None
            protocal_relate_protocal_id = try_parse_int(protocal_relate_protocal_id)
            if protocal_relate_protocal_id and protocal_relate_protocal_id != 0:
                protocal_relate_protocal = get_object_or_404(Protocal, pk=protocal_relate_protocal_id)

            cur_relate_prototal_id = 0;
            if cur_protocal and cur_protocal.relate_protocal:
                cur_relate_prototal_id = cur_protocal.relate_protocal.id;
            if protocal_relate_protocal and protocal_relate_protocal.id != cur_relate_prototal_id:
                if protocal_relate_protocal.relate_protocal:
                    raise ValidationError("relate protocal allready has other protocal be realted.");
            
            protocal_type = get_object_or_404(ProtocalType, pk=protocal_type_id) 
            
            if cur_protocal:
                last_relate_protocal = cur_protocal.relate_protocal
                if last_relate_protocal and ( protocal_relate_protocal == None or last_relate_protocal.id != protocal_relate_protocal.id):
                    Protocal.objects.filter(pk=last_relate_protocal.id).update( relate_protocal = None)
                    
                Protocal.objects.filter(pk=protocal_id).update(name = strip(protocal_name),
                                    desc = protocal_desc,
                                    module = cur_module,
                                    protocal_id = protocal_protocal_id,
                                    protocal_unique_id = protocal_protocal_unique_id,
                                    type = protocal_type,
                                    namespace = strip(protocal_namespace),
                                    relate_protocal = protocal_relate_protocal,
                                    )
                if protocal_relate_protocal:
                    Protocal.objects.filter(pk=protocal_relate_protocal.id).update( relate_protocal = cur_protocal)
            else:
                protocal = Protocal(name = strip(protocal_name),
                                    desc = protocal_desc,
                                    module = cur_module,
                                    protocal_id = protocal_protocal_id,
                                    protocal_unique_id = protocal_protocal_unique_id,
                                    type = protocal_type,
                                    namespace = strip(protocal_namespace),
                                    relate_protocal = protocal_relate_protocal,
                                    )
    
                protocal.save()
                
                Protocal.objects.filter(pk=protocal_relate_protocal_id).update( relate_protocal = protocal)
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        cur_module = get_module_by_id(module_id)
        if cur_module == None:
            return index(request)

        cur_project = get_object_or_404(Project, pk=project_id)
        cur_protocal = Protocal.objects.filter(id=protocal_id).first()
        modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
        protocal_types = ProtocalType.objects.all()
        segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(project = cur_project))).order_by('-is_basic','-show_priority','-timestamp')
        segment_proto_types = SegmentProtoType.objects.all()
        relate_protocals = Protocal.objects.filter(module = cur_module).exclude(id = protocal_id).filter(relate_protocal = None)
        
        return render(request, 'protocal_new.html',{'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'cur_protocal':cur_protocal,
                                                  'modules':modules,
                                                  'protocal_types':protocal_types,
                                                  'segment_types':segment_types,
                                                  'segment_proto_types':segment_proto_types,
                                                  'relate_protocals':relate_protocals,
                                                  
                                                  }) 

def protocal_edit(request,project_id,protocal_id):
    cur_project = get_object_or_404(Project, pk=project_id)
    cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
    cur_module = try_get_module(cur_protocal)
    if cur_module == None:
        return index(request)

    return protocal_create(request,project_id,cur_module.id,cur_protocal.id)

def protocal_delete(request):
    if request.method == 'POST': 
        protocal_id = request.POST['protocal_id'] 
        cur_protocal = get_object_or_404(Protocal, pk=protocal_id)

        if cur_protocal:
            relate_protocal = Protocal.objects.filter(relate_protocal = cur_protocal)
            if relate_protocal:
                relate_protocal.relate_protocal = None
                relate_protocal.update()
            cur_protocal.delete()
        else:
            raise ValidationError("protocal_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  


# segments ------------------------------------------------------------------------------------
def segments_detail(request,protocal_id):
    cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
    cur_module = try_get_module(cur_protocal)
    if cur_module == None:
        return index(request)

    cur_project = cur_module.project
    
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    segments = Segment.objects.filter(protocal = cur_protocal).order_by('timestamp')
    protocal_types = ProtocalType.objects.all()
    segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(project = cur_project))).order_by('-is_basic','-show_priority', '-timestamp')
    segment_proto_types = SegmentProtoType.objects.all()
    relative_protocals = Protocal.objects.filter(module = cur_module)
    
    return render(request, 'segments_detail.html',{'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'cur_protocal':cur_protocal,
                                                  'modules':modules,
                                                  'segments':segments,
                                                  'protocal_types':protocal_types,
                                                  'segment_types':segment_types,
                                                  'segment_proto_types':segment_proto_types,
                                                  'relative_protocals':relative_protocals,
                                                  })

def segment_create(request,protocal_id,segment_id = 0):
    if request.method == 'POST': 
        cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
        cur_segment = Segment.objects.filter(pk=segment_id)
        cur_module = try_get_module(cur_protocal)
        if cur_module == None:
            return index(request)
        
        segment_name = request.POST['segment_name'] 
        segment_desc = request.POST['segment_desc'] 
        segment_type_id = request.POST['segment_type_id'] 
        segment_extra_type1_id = request.POST['segment_extra_type1_id'] 
        segment_extra_type2_id = request.POST['segment_extra_type2_id'] 
        segment_protocal_type_id = request.POST['segment_protocal_type_id'] 
        segment_namespace = cur_protocal.namespace + "." + segment_name
        segment_default_value = request.POST['segment_default_value']
        
        if not segment_name:
            raise ValidationError("segment_name should not be null.");
        if not segment_desc:
            raise ValidationError("segment_desc should not be null.");
        if not segment_protocal_type_id :
            raise ValidationError("segment_protocal_type_id should not be null.");
        if not segment_type_id:
            raise ValidationError("segment_type should not be null.");
        else:
            
            segment_type = get_object_or_404(SegmentType, pk=segment_type_id) 
            segment_extra_type1 = get_object_or_404(SegmentType, pk=segment_extra_type1_id) 
            segment_extra_type2 = get_object_or_404(SegmentType, pk=segment_extra_type2_id) 
            segment_protocal_type = get_object_or_404(SegmentProtoType, pk=segment_protocal_type_id) 
            if try_parse_int(segment_default_value):
                enumsegemet = get_object_or_404(EnmuSegment, pk=segment_default_value)
            else:
                enumsegemet = None
            
            if cur_segment:
                cur_segment.update(name = strip(segment_name),
                                    desc = segment_desc,
                                    protocal = cur_protocal,
                                    protocal_type = segment_protocal_type,
                                    type = segment_type,
                                    extra_type1 = segment_extra_type1,
                                    extra_type2 = segment_extra_type2,
                                    namespace = strip(segment_namespace),
                                    defaultEnum = enumsegemet
                                    )
            else:
                segment = Segment(name = strip(segment_name),
                                    desc = segment_desc,
                                    protocal = cur_protocal,
                                    protocal_type = segment_protocal_type,
                                    type = segment_type,
                                    extra_type1 = segment_extra_type1,
                                    extra_type2 = segment_extra_type2,
                                    namespace = strip(segment_namespace),
                                    defaultEnum = enumsegemet
                                    )
    
                segment.save()
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
        cur_segment = Segment.objects.filter(id=segment_id).first()
        cur_module = try_get_module(cur_protocal)
        if cur_module == None:
            return index(request)

        segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(module=cur_module))).order_by('-is_basic','-show_priority','-timestamp')
        segment_types = segment_types.exclude(~Q(protocal = None) , ~Q(protocal = cur_protocal))
        segment_proto_types = SegmentProtoType.objects.all()

        for segment_type in segment_types:
            if segment_type.provider_type == 1:
                enum = Enum.objects.filter(type = segment_type)
                enumsegments = EnmuSegment.objects.filter(belong = enum)
                segment_type.enumsegments = enumsegments

        return render(request, 'segment_create_dialog.html',{
                                                  'cur_protocal':cur_protocal,
                                                  'cur_segment':cur_segment,
                                                  'segment_proto_types':segment_proto_types,
                                                  'segment_types':segment_types,
                                                  }) 

def segment_edit(request,segment_id):
    cur_segment = get_object_or_404(Segment, pk=segment_id)
    return segment_create(request,cur_segment.protocal.id,cur_segment.id)

def segment_delete(request):
    if request.method == 'POST': 
        segment_id = request.POST['segment_id'] 
        cur_segment = get_object_or_404(Segment, pk=segment_id)

        if cur_segment:
            cur_segment.delete()

        else:
            raise ValidationError("segment_id should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>")  

# module ----------------------------------------------------------
def module_create(request,project_id):
    if request.method == 'POST': 
        cur_project = get_object_or_404(Project, pk=project_id)
        module_name = request.POST['module_name'] 
        module_desc = request.POST['module_desc'] 
        module_modulename = request.POST['module_modulename']
        module_namespace = cur_project.namespace + "." + module_modulename

        if module_name and module_desc and module_modulename:
            module = Module(
                name = module_modulename,
                namedesc = strip(module_name),
                desc = module_desc,
                project = cur_project,
                namespace = module_namespace)
            module.save()
        else:
            raise ValidationError("name or desc should not be null.");
        
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>") 

def module_detail(request,module_id):
    cur_module = get_module_by_id(module_id)
    if cur_module == None:
        return index(request)

    cur_project = cur_module.project
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    protocals = Protocal.objects.filter(module = cur_module).order_by('-timestamp')
    enums = Enum.objects.filter(module = cur_module).order_by('-timestamp')
    customtypes = CustomType.objects.filter(module = cur_module).order_by('-timestamp')
    protocal_types = ProtocalType.objects.all()
    segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(project = cur_project))).order_by('-is_basic','-show_priority', '-timestamp')
    segment_proto_types = SegmentProtoType.objects.all()
    relative_protocals = Protocal.objects.filter(module = cur_module)

    protocals = protocals.order_by('protocal_id')
    return render(request, 'project_detail.html',{'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'modules':modules,
                                                  'protocals':protocals,
                                                  'enums':enums,
                                                  'customtypes':customtypes,
                                                  'protocal_types':protocal_types,
                                                  'segment_types':segment_types,
                                                  'segment_proto_types':segment_proto_types,
                                                  'relative_protocals':relative_protocals,
                                                  })


def project_config_download(request):
    export_setting = ExporterSetting.objects.first()
    def file_iterator(file_path, chunk_size=512):
        with open(file_path,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = 'config_lua.zip'                
    the_file_path = export_setting.export_path + '/config'+  '/archive/' + the_file_name
#     print 'the_file_path:' + the_file_path
    file_size = os.path.getsize(the_file_path)
    print 'file size:' + str(file_size)
    response = StreamingHttpResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    response['Content-Length'] = file_size
    return response


def project_export_config(request):
    if request.method == 'POST': 

        export_setting = ExporterSetting.objects.first()

        try:
            export_config.do_export(export_setting.export_path)
        except Exception,e:
            utils.print_trace()
            raise e
        finally:
            pass

        return HttpResponse("<h1>Export successfully .</h1>")  
    else:
        return HttpResponse("<h1>Invalid request.</h1>") 