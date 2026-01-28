import datetime
import re
from dis import Instruction

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from manpower.fields import ListTextWidget
from manpower.models import Division, Profile
from .models import *
from django.db.models import Q
from functools import reduce
import operator
from django.contrib.auth import backends, get_user_model
from django.contrib.auth.models import Group


TASK_STATUS =(
    ("1", "Created"),
    ("2", "Assigned"),
    ("3", "Completed"),
)

consultancy_request_status =(
    ("all", "All Requests"),
    ("pending", "Pending Requests"),
    ("assigned", "Consultant Assigned"),
)
task_category = (
    ("","ALL"),
    ("SAW","SAW"),
    ("CEW","CEW"),
    ("DocumentReview","DocumentReview"),
)

recommendation = (
    ("", "Select"),
    ("Yes", "Yes"),
    ("No", "No")
)
class DateInput(forms.DateInput):
    input_type = 'date'

class YearFilterForm(forms.Form):
    CURRENT_YEAR = datetime.datetime.now().year
    YEAR_CHOICES = [(y, y) for y in range(CURRENT_YEAR, 2014, -1)]

    year = forms.ChoiceField(choices=YEAR_CHOICES, label="Select Year")

class EventForm(ModelForm):
    unit = forms.ChoiceField(choices=UNIT, label="Unit", required=False)
    facility = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    elevation = forms.CharField(label='Elevation',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    room_no = forms.CharField(label='Room No',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    additional_location_info = forms.CharField(label='Additional Information of location',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    event_date = forms.DateField(label='Even Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    event_time = forms.TimeField(label='Event Time', required= False,  widget=forms.TimeInput(attrs={'type': 'time'}))
    event_category = forms.ChoiceField(choices=EVENT_CATEGORY, label="Event Category", required=False)
    regulatory_norms_violation = forms.BooleanField(label='Violation of regulatory norms and regulations',required=False)
    description = forms.CharField(label='Event Description',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    direct_cause = forms.CharField(label='Direct Cause',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    elimination_suggestion = forms.CharField(label='Elimination Suggestion',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    responsible_dept = forms.ModelChoiceField(queryset=DepartmentShop.objects.all(), label='Responsible Department', required=False)
    plant_status = forms.ChoiceField(choices=PLANT_STATUS, label="Plant Status", required=False)
    uploader_shop = forms.ModelChoiceField(queryset=DepartmentShop.objects.all(), label='Reporter Shop/Department', required=False)
    uploader_organization = forms.CharField(label='Reporter Organization',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_designation = forms.CharField(label='Reporter Designation',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_phone = forms.CharField(label='Reporter Phone',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_bioID = forms.CharField(label='Reporter Bio ID',required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    information_source = forms.ChoiceField(choices=INFORMATION_SOURCE, label='Information Source',required=False)
    keep_identity_confidential = forms.BooleanField(label='Keep Identity Confidential',required=False)
    supporting_file_1 = forms.FileField(label='Select file 1', required=False)
    supporting_file_2 = forms.FileField(label='Select file 2', required=False)
    supporting_file_3 = forms.FileField(label='Select file 3', required=False)
    supervisor = forms.ModelMultipleChoiceField(queryset=User.objects.filter(profile__is_supervisor=True),
                                                label="Select Supervisor", required=False)
    executor = forms.ModelMultipleChoiceField(queryset=User.objects.filter(profile__is_executor=True),
                                                   label="Select Executor", required=False)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        if(kwargs.get('instance')):
            instance = kwargs.get('instance')
            self.fields['supervisor'].initial = instance.supervisor.all()
            self.fields['executor'].initial = instance.executor.all()
            # self.fields['milestone_id'].widget.attrs['readonly'] = True
            # self.fields['milestone_id'].widget.attrs['class'] = 'readonly_field'

    class Meta:
        model = Event
        exclude = ('uploaded_by', 'uploaded_date', 'action_taken', 'action_to_prevent_recurrence_event', 'approval_status', 'approved_by', 'approval_date', 'updated_by', 'updated_date', 'resolution_status', 'resolved_by', 'resolved_date', 'resolver_remarks', 'submission_status')

class EventSearchForm(ModelForm):
    event_category = forms.ChoiceField(choices=EVENT_CATEGORY, label="Event Category", required=False)
    facility = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    description = forms.CharField(label='Event Description', required=False,
                                  widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}))

    class Meta:
        model = Event
        fields = ('event_category', 'facility', 'description')

class EventResolutionForm(ModelForm):
    action_taken = forms.CharField(label='Action Taken', required=False,
                                      widget=forms.Textarea(attrs={'rows': 3, 'cols': 50}))
    action_to_prevent_recurrence_event = forms.CharField(label='Actions to prevent recurrence event', required=False,
                                                         widget=forms.Textarea(attrs={'rows': 3, 'cols': 50}))
    resolution_status = forms.ChoiceField(choices=RESOLUTION_STATUS, label='Resolution Status', required=True)
    resolver_remarks = forms.CharField(label='Remarks', required=True,
                                  widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))

    class Meta:
        model = Event
        fields = ('action_taken', 'action_to_prevent_recurrence_event', 'resolution_status', 'resolver_remarks')