# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.http.response import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from string import strip

from protocal.models import *

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
        protocal_route = request.POST['protocal_route'] 
        protocal_protocal_id = request.POST['protocal_id'] 
        protocal_protocal_unique_id = try_parse_int(protocal_protocal_id)
        protocal_type_id = request.POST['protocal_type_id'] 
        protocal_relate_protocal_id = request.POST['protocal_relate_protocal_id'] 
        protocal_namespace = cur_module.namespace + "." + protocal_name
        
        if not protocal_name or strip(protocal_name) == '':
            raise ValidationError("protocal_name should not be null.");
        if not protocal_desc:
            raise ValidationError("protocal_desc should not be null.");
#         if not protocal_route or strip(protocal_route) == '':
#             raise ValidationError("protocal_route should not be null.");
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
                                    route = strip(protocal_route),
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
                                    route = strip(protocal_route),
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