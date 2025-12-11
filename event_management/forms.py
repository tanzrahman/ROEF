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

class EventForm(ModelForm):
    unit = forms.CharField(label='Unit',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    facility = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    elevation = forms.CharField(label='Elevation',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    room_no = forms.CharField(label='Room No',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    additional_location_info = forms.CharField(label='Additional Information of location',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    event_date = forms.DateField(label='Even Date', required=False, widget=DateInput)
    event_time = forms.TimeField(label='Event Time', required= False, widget=forms.TimeInput(attrs={'class': 'time-text-input'}))
    event_category = forms.CharField(label='Event Category',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    safety_importance = forms.BooleanField(label='Safety Importance',required=True)
    comment_if_safety_importance = forms.CharField(label='Comment of Safety Importance',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    description = forms.CharField(label='Event Description',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    direct_cause = forms.CharField(label='Direct Cause',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    action_taken = forms.BooleanField(label='Action Taken',required=True)
    comment_if_action_taken = forms.CharField(label='Details of Taken Action',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    elimination_suggestion = forms.CharField(label='Elimination Suggestion',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    responsible_dept = forms.ModelChoiceField(queryset=Division.objects.all(), label='Responsible Department', required=False)
    plant_status = forms.CharField(label='Plant Status',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploaded_by = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    upload_date = forms.DateField(label='Planned end date', required=False, widget=DateInput)
    uploader_shop = forms.ModelChoiceField(queryset=Division.objects.all(), label='Reporter Shop/Department', required=False)
    uploader_organization = forms.CharField(label='Reporter Organization',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_designation = forms.CharField(label='Reporter Designation',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_phone = forms.CharField(label='Reporter Phone',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    uploader_bioID = forms.CharField(label='Reporter Bio ID',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    information_source = forms.CharField(label='Information Source',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    keep_identity_confidential = forms.BooleanField(label='Keep Identity Confidential',required=True)

    class Meta:
        model = Event
        exclude = ('upload_by', 'upload_date')

class EventSearchForm(ModelForm):
    event_category = forms.CharField(label='Event Category',required=True, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    facility = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    description = forms.CharField(label='Event Description', required=True,
                                  widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))

    class Meta:
        model = Event
        fields = ('event_category', 'facility', 'description')