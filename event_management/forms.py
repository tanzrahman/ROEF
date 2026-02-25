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
    description = forms.CharField(label='Event Description',required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}))
    direct_cause = forms.CharField(label='Direct Cause',required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}))
    elimination_suggestion = forms.CharField(label='Elimination Suggestion',required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}))
    responsible_dept = forms.ModelChoiceField(queryset=DepartmentShop.objects.all(), label='Responsible Department', required=False)
    plant_status = forms.ChoiceField(choices=PLANT_STATUS, label="Plant Status", required=False)
    information_source = forms.ChoiceField(choices=INFORMATION_SOURCE, label='Information Source',required=False)
    keep_identity_confidential = forms.BooleanField(label='Keep Identity Confidential',required=False)
    supporting_file_1 = forms.FileField(label='Select file 1', required=False)
    supporting_file_2 = forms.FileField(label='Select file 2', required=False)
    supporting_file_3 = forms.FileField(label='Select file 3', required=False)
    supervisor = forms.ModelMultipleChoiceField(queryset=User.objects.filter(profile__is_supervisor=True),
                                                label="Select Supervisor", required=False)
    executor = forms.ModelMultipleChoiceField(queryset=User.objects.filter(profile__is_executor=True),
                                                   label="Select Executor", required=False)
    eae_mom_file = forms.FileField(label='MoM file', required=False)
    type_of_safety = forms.ModelMultipleChoiceField(queryset=SafetyType.objects.all(), label='Type of Safety', required=False)
    level_code = forms.ModelMultipleChoiceField(queryset=LevelCode.objects.all(), label='Level Code', required=False)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        if(kwargs.get('instance')):
            instance = kwargs.get('instance')
            self.fields['supervisor'].initial = instance.supervisor.all()
            self.fields['executor'].initial = instance.executor.all()
            self.fields['type_of_safety'].initial = instance.type_of_safety.all()
            self.fields['level_code'].initial = instance.level_code.all()
            # self.fields['milestone_id'].widget.attrs['readonly'] = True
            # self.fields['milestone_id'].widget.attrs['class'] = 'readonly_field'

    class Meta:
        model = Event
        exclude = ('uploader_organization','uploader_shop', 'uploader_designation', 'uploader_phone', 'event_code', 'uploaded_by', 'uploaded_date', 'action_taken', 'action_to_prevent_recurrence_event', 'approval_status', 'approved_by', 'approval_date', 'updated_by', 'updated_date', 'resolution_status', 'resolved_by', 'resolved_date', 'resolver_remarks', 'submission_status', 'eae_mom_id', 'eae_mom_date', 'is_guest')


class EventGoodPracticeForm(ModelForm):
    name = forms.ChoiceField(choices=GP_NAME, label='Name', required=False)
    description = forms.CharField(label='Description',required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}))
    log_book_no = forms.CharField(label='Log Book No', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 50}))
    keywords = forms.CharField(label='Keywords',required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}))
    reactor_type = forms.ChoiceField(choices=REACTOR_TYPE, label='Reactor Type',required=False)
    npp_activities = forms.ChoiceField(choices=NPP_ACTIVITIES, label='NPP Activities', required=False)
    main_activities = forms.ChoiceField(choices=MAIN_ACTIVITIES, label='Main Activities', required=False)
    general_activities = forms.ChoiceField(choices=GENERAL_ACTIVITIES, label='General Activities', required=False)
    problem_elimination_specification = forms.ChoiceField(choices=GP_APPLICATION_FOR_PROBLEM_ELIMINATION, label='Problem Elimination Specification',required=False)
    gp_applications = forms.ChoiceField(choices=GP_APPLICATION, label='Good Practice Applications', required=False)
    expert_assessment = forms.ChoiceField(choices=EXPERT_ASSESSMENT_ON_APPLICATION, label='Expert Assessment', required=False)
    information_source = forms.ChoiceField(choices=INFORMATION_SOURCE, label='Information Source',required=False)
    distribution_recommendation = forms.ChoiceField(choices=GP_DISTRIBUTION_RECOMMENDATION, label='Recommendation for Distribution', required=False)

#     def __init__(self, *args, **kwargs):
#         super(EventGoodPracticeForm, self).__init__(*args, **kwargs)
#
#         if(kwargs.get('instance')):
#             instance = kwargs.get('instance')
#             self.fields['supervisor'].initial = instance.supervisor.all()
#             self.fields['executor'].initial = instance.executor.all()
#             # self.fields['milestone_id'].widget.attrs['readonly'] = True
#             # self.fields['milestone_id'].widget.attrs['class'] = 'readonly_field'
    class Meta:
        model = EventGoodPractice
        exclude = ('uploader_organization','uploader_shop', 'uploader_designation', 'uploader_phone', 'uploader_bioID', 'uploaded_by', 'uploaded_date', 'updated_by', 'updated_date')


class EventSearchForm(ModelForm):
    event_category = forms.ChoiceField(choices=EVENT_CATEGORY, label="Event Category", required=False)
    facility = forms.ModelChoiceField(queryset=Division.objects.all(), required=False)
    description = forms.CharField(label='Event Description', required=False,
                                  widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}))

    class Meta:
        model = Event
        fields = ('event_category', 'facility', 'description')

class GPSearchForm(ModelForm):
    name = forms.ChoiceField(choices=GP_NAME, label='Name', required=False)
    description = forms.CharField(label='Description', required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}))
    reactor_type = forms.ChoiceField(choices=REACTOR_TYPE, label='Reactor Type', required=False)
    class Meta:
        model = EventGoodPractice
        fields = ('name', 'description', 'reactor_type')

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