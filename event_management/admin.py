from django.contrib import admin
from event_management.models import *

admin.site.register(Event)
admin.site.register(EventGoodPractice)
admin.site.register(SafetyType)
admin.site.register(LevelCode)