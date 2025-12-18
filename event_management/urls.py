from django.contrib import admin
from django.urls import path, include

import event_management.views as event_management

urlpatterns = [
	path('', event_management.homepage, name='event_management'),
	path('<action>', event_management.event_request_handler,name='event_request_handler'),
	path('<action>/<int:event_id>', event_management.event_request_handler, name='event_request_handler'),
	path('<action>/<int:event_id>/file/<int:file_no>/', event_management.event_request_handler, name='event_view'),

	#path('upload',event_management.upload_event,name='upload_event')

]