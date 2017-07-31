# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.http.response import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from datetime import datetime
from string import strip

from protocal.models import *
from protocal import export_utils, utils
from protocal.utils import try_parse_int

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
	modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
	protocals = Protocal.objects.filter(module__in = modules).order_by('-timestamp')
	protocal_types = ProtocalType.objects.all()
	return render(request, 'project_detail.html', { 'cur_project':cur_project,
													'modules':modules,
													'protocals':protocals,
													'protocal_types':protocal_types,
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
    the_file_path = export_setting.export_path + cur_project.namespace + '/archive/' + the_file_name
#     print 'the_file_path:' + the_file_path
    file_size = os.path.getsize(the_file_path)
    print 'file size:' + str(file_size)
    response = StreamingHttpResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    response['Content-Length'] = file_size
    return response

# protocal --------------------------------------------------------
def protocal_detail(request,protocal_id):
    cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
    segments = Segment.objects.filter(protocal = cur_protocal)
    return render(request, 'protocal_detail_dialog.html',{
                                                  'cur_protocal':cur_protocal,
                                                  'segments':segments,
                                                  }) 

def protocal_create(request,module_id,protocal_id = 0):
    if request.method == 'POST': 
        cur_module = get_object_or_404(Module, pk=module_id)
        cur_project = cur_module.project
        cur_protocal = Protocal.objects.filter(pk=protocal_id).first()
        
        protocal_name = request.POST['protocal_name'] 
        protocal_desc = request.POST['protocal_desc'] 
        protocal_protocal_id = request.POST['protocal_id'] 
        protocal_protocal_unique_id = try_parse_int(protocal_protocal_id)
        protocal_type_id = request.POST['protocal_type_id'] 
        protocal_relate_protocal_id = request.POST['protocal_relate_protocal_id'] 
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
        cur_module = get_object_or_404(Module, pk=module_id)
        cur_project = cur_module.project
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

def protocal_edit(request,protocal_id):
    cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
    return protocal_create(request,cur_protocal.module.id,cur_protocal.id)

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
    cur_module = cur_protocal.module
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
        cur_module = cur_protocal.module
        cur_project = cur_module.project
        
        segment_name = request.POST['segment_name'] 
        segment_desc = request.POST['segment_desc'] 
        segment_type_id = request.POST['segment_type_id'] 
        segment_extra_type1_id = request.POST['segment_extra_type1_id'] 
        segment_extra_type2_id = request.POST['segment_extra_type2_id'] 
        segment_protocal_type_id = request.POST['segment_protocal_type_id'] 
        segment_namespace = cur_protocal.namespace + "." + segment_name
        
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
            
            if cur_segment:
                cur_segment.update(name = strip(segment_name),
                                    desc = segment_desc,
                                    protocal = cur_protocal,
                                    protocal_type = segment_protocal_type,
                                    type = segment_type,
                                    extra_type1 = segment_extra_type1,
                                    extra_type2 = segment_extra_type2,
                                    namespace = strip(segment_namespace),
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
                                    )
    
                segment.save()
        return HttpResponse("<h1>Created successfully .</h1>")  
    else:
        cur_protocal = get_object_or_404(Protocal, pk=protocal_id)
        cur_segment = Segment.objects.filter(id=segment_id).first()
        cur_module = cur_protocal.module
        cur_project = cur_module.project
        segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(project = cur_project))).order_by('-is_basic','-show_priority','-timestamp')
        segment_proto_types = SegmentProtoType.objects.all()
        
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
    cur_module = get_object_or_404(Module, pk=module_id)
    cur_project = cur_module.project
    modules = Module.objects.filter(project = cur_project).order_by('-timestamp')
    protocals = Protocal.objects.filter(module = cur_module).order_by('-timestamp')
    protocal_types = ProtocalType.objects.all()
    segment_types = SegmentType.objects.filter(Q(is_basic = True) | (Q(is_basic=False) and Q(project = cur_project))).order_by('-is_basic','-show_priority', '-timestamp')
    segment_proto_types = SegmentProtoType.objects.all()
    relative_protocals = Protocal.objects.filter(module = cur_module)
    
    return render(request, 'project_detail.html',{'cur_project':cur_project,
                                                  'cur_module':cur_module,
                                                  'modules':modules,
                                                  'protocals':protocals,
                                                  'protocal_types':protocal_types,
                                                  'segment_types':segment_types,
                                                  'segment_proto_types':segment_proto_types,
                                                  'relative_protocals':relative_protocals,
                                                  })