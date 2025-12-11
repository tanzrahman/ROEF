from event_management.models import *
import datetime
from system_log.models import EventLog
from django import template

register = template.Library()

@register.filter(name='event')
def task_change_log(event):
    try:
        task_logs = EventLog.objects.filter(event=event).order_by('-created_at')
        if(task_logs.count()>0):
            return task_logs
        else:
            return None
    except Exception as e:
        print(e)
        return None