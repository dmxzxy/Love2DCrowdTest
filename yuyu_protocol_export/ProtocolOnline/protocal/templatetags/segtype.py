
from django import template
register = template.Library()

@register.filter(name='segtype_a')
def segtype_a(segment_type):
    if segment_type.is_basic:
        return segment_type.name
    else:
#         return "<a class='show_segment_class_detail' id='{{ segment.type.id }}' title='{{ segment.type.name }}'>{{ segment.type }}</a>"
        return "<a class='show_segment_class_detail' id='%d' title='%s'>%s</a>"%(segment_type.id,segment_type.name,segment_type.name)
    
@register.filter(name='segtype')
def segtype(segment):
    if segment.type.name == 'map':
        return 'map&lt;' + segtype_a(segment.extra_type1) + ',' + segtype_a(segment.extra_type2) + '&gt;'
    return segtype_a(segment.type)