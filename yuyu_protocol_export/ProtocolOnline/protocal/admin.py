# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Project)
admin.site.register(Module)
admin.site.register(Protocal)
admin.site.register(ProtocalType)
admin.site.register(SegmentType)
admin.site.register(SegmentProtoType)
admin.site.register(Segment)
admin.site.register(CustomSegmentType)
admin.site.register(CustomSegmentTypeSegment)
admin.site.register(ExporterSetting)
