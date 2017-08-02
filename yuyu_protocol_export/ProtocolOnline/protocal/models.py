# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ExporterSetting(models.Model):
    export_path = models.CharField(max_length = 150,blank = False)
    def __unicode__(self):
        return self.export_path

class Project(models.Model):
    title = models.CharField(max_length = 150,blank = False)
    namespace = models.CharField(max_length = 150,blank = False,unique = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_exporting = models.BooleanField(default = False)
    is_modified = models.BooleanField(default=True)
    def __unicode__(self):
        return self.title

class ProjectExport(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    version = models.CharField(max_length = 150,blank = False,unique = True)
    EXPORT_STATUS_CHOICES = (
        (1, 'Prepare'),
        (2, 'Successfully'),
        (3, 'Failed'),
    )
    status = models.IntegerField(choices=EXPORT_STATUS_CHOICES,default = 1)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.version
    
class Module(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    namedesc = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    namespace = models.CharField(max_length = 100,blank = False,unique = True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self): 
        return self.name
    
class ProtocalType(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    def __unicode__(self):
        return self.name
    
class Protocal(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    namespace = models.CharField(max_length = 100,blank = False,unique = True)
    protocal_id = models.IntegerField()
    protocal_unique_id = models.IntegerField(unique = True)
    module = models.ForeignKey(Module,on_delete=models.CASCADE)
    type = models.ForeignKey(ProtocalType)
    relate_protocal = models.ForeignKey("self",null = True)
    is_modified = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name
    
class SegmentType(models.Model):
    name = models.CharField(max_length = 100,blank = False,unique = True)
    desc = models.CharField(max_length = 150,blank = False)
    is_basic = models.BooleanField(default=True)
    project = models.ForeignKey(Project,null=True,blank = True,default=None)
    module = models.ForeignKey(Module,on_delete=models.CASCADE,null=True,default=None)
    protocal = models.ForeignKey(Protocal,on_delete=models.CASCADE,null=True,default=None)
    show_priority = models.IntegerField(default = 0)
    provider_type = models.IntegerField(default = 0) # 0 basic 1 enum 2 customtype
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name
        
class SegmentProtoType(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    def __unicode__(self):
        return self.name
        
class Segment(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    namespace = models.CharField(max_length = 100,blank = False,unique = True)
    protocal = models.ForeignKey(Protocal,on_delete=models.CASCADE)
    type = models.ForeignKey(SegmentType)
    extra_type1 = models.ForeignKey(SegmentType,null=True,blank = True,default=None,related_name='segment_extra_type_1')
    extra_type2 = models.ForeignKey(SegmentType,null=True,blank = True,default=None,related_name='segment_extra_type_2')
    protocal_type = models.ForeignKey(SegmentProtoType)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name    

class CustomType(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    type = models.ForeignKey(SegmentType,on_delete=models.CASCADE,null=True,default=None)
    module = models.ForeignKey(Module,on_delete=models.CASCADE)
    belong = models.ForeignKey(Protocal,on_delete=models.CASCADE,null=True,default=None)
    namespace = models.CharField(max_length = 100,blank = False,unique = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name    

class CustomTypeSegment(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    type = models.ForeignKey(SegmentType)
    protocal_type = models.ForeignKey(SegmentProtoType)
    belong = models.ForeignKey(CustomType,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name   

class Enum(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    type = models.ForeignKey(SegmentType,on_delete=models.CASCADE,null=True,default=None)
    namespace = models.CharField(max_length = 100,blank = False,unique = True)
    module = models.ForeignKey(Module,on_delete=models.CASCADE)
    belong = models.ForeignKey(Protocal,on_delete=models.CASCADE,null=True,default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name    

class EnmuSegment(models.Model):
    name = models.CharField(max_length = 100,blank = False)
    desc = models.CharField(max_length = 150,blank = False)
    value = models.IntegerField()
    belong = models.ForeignKey(Enum,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name    