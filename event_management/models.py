import datetime
import os
from inspect import Signature

from django.db import models
from django.db.transaction import mark_for_rollback_on_error
from django.utils import timezone
from manpower.models import *


UNIT = (
    ("", "-------"),
    ("unit_1", "Unit 1"),
    ("unit_2", "Unit 2"),
    ("common", "Common Plant"),
)

EVENT_CATEGORY = (
    ("", "-------"),
    ("LLE", "Low Level Event"),
    ("NME", "NME"),
    ("EAE", "Extended Analysis of Event"),
    ("Defect", "Defect"),
    ("Deviation", "Deviation"),
    ("Violation", "Violation"),
)

INFORMATION_SOURCE = (
    ("", "-------"),
    ("internal", "Internal"),
    ("external", "External"),
)

PLANT_STATUS = (
    ("", "-------"),
    ("commissioning", "Commissioning"),
    ("operation", "Operation"),
    ("refuelling", "Refuelling"),
    ("power_outage", "Power Outage"),
)

RESOLUTION_STATUS = (
    ("", "-------"),
    ("resolved", "Resolved"),
    ("working", "Working"),
    ("test", "Test"),
    ("demo", "Demo"),
)

GP_NAME = (
    ("", "-------"),
    ("1", "Increasing of maintenance & repair quality"),
    ("2", "Upgrading of floor drain system"),
    ("3", "Increasing of effectiveness of engineering support"),
    ("4", "Increasing of effectiveness of floor drain processing by reducing the ammonia content by ozone treatment"),
    ("5", "Others"),
)

REACTOR_TYPE = (
    ("", "-------"),
    ("1", "VVER-440"),
    ("2", "VVER-1000/1200"),
    ("3", "RBMK"),
    ("4", "EHC"),
    ("5", "Fast Neutron Reactor"),
    ("6", "Others"),
)

NPP_ACTIVITIES = (
    ("", "-------"),
    ("1", "Main Activities"),
    ("2", "General Activities"),
)

MAIN_ACTIVITIES = (
    ("", "-------"),
    ("1", "Management, organisation and administration"),
    ("2", "Operation"),
    ("3", "Maintenance and repair"),
    ("4", "Engineering and technical support"),
    ("5", "Radiation protection"),
    ("6", "Application of operational experience"),
    ("7", "Process chemistry"),
    ("8", "Personnel trainings and qualification"),
    ("9", "Fire protection"),
    ("10", "Emergency planning and preparedness"),
    ("11", "Commissioning"),
    ("12", "Safety culture"),
)

GENERAL_ACTIVITIES = (
    ("", "-------"),
    ("1", "Personnel operation"),
    ("2", "Self-assessment"),
    ("3", "Occupational safety"),
    ("4", "Monitoring of the NS state"),
    ("5", "Production management"),
    ("6", "Equipment operation and state"),
    ("7", "Management of severe accidents"),
    ("8", "Others"),
)

GP_APPLICATION_FOR_PROBLEM_ELIMINATION = (
    ("", "-------"),
    ("1", "Prevention of human errors"),
    ("2", "Improvement of personnel actions"),
    ("3", "Decreasing of radiation exposure"),
    ("4", "Inspection/prevention of leakages"),
    ("5", "Prevention of foreign objects ingress"),
    ("6", "Inspection/assessment of erosion-corrosion wear"),
    ("7", "Assessment/prevention of ageing"),
    ("8", "Risks/ fire prevention/consequences mitigation"),
    ("9", "Improvement of system/equipment operation"),
    ("10", "Reducing of radioactive waste"),
    ("11", "Improvement/management of process chemistry"),
    ("12", "Prevention/mitigation of probability of electrical equipment failure"),
    ("13", "Others"),
)

GP_APPLICATION = (
    ("", "-------"),
    ("1", "Documentation (instructions, guidelines, check-lists, etc."),
    ("2", "Software"),
    ("3", "Database"),
    ("4", "Training procedures"),
    ("5", "New systems/equipment"),
    ("6", "Upgrading of existing systems and equipment, practices"),
    ("7", "New designs"),
    ("8", "Others"),
)

EXPERT_ASSESSMENT_ON_APPLICATION = (
    ("", "-------"),
    ("1", "The problem is solved"),
    ("2", "The problem scale is reduced"),
    ("3", "Useful information"),
)

GP_IDENTIFICATION_SOURCE = (
    ("", "-------"),
    ("1", "Analysis of operational experience"),
    ("2", "WANO peer review"),
    ("3", "OSART mission"),
    ("4", "Workshop/visit exchange at NPP"),
    ("5", "NPP inspection/checking"),
    ("6", "NPP management meeting"),
    ("7", "Decision (technical decision)"),
    ("8", "Others"),
)

GP_DISTRIBUTION_RECOMMENDATION = (
    ("", "-------"),
    ("1", "All NPPs"),
    ("2", "VVER"),
    ("3", "RBMK"),
    ("4", "EHC"),
    ("5", "During designing and engineering"),
    ("6", "Others"),
)

# Create your models here.

class SystemParameter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'system_parameter'


class System(models.Model):
    system_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    code = models.CharField(max_length=256, blank=True, null=True)
    short_description = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = 'system'

    def __str__(self):
        return str(self.name)

class SubSystem(models.Model):
    subsystem_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    system = models.ForeignKey(System, on_delete=models.DO_NOTHING,blank=True,null=True)

    class Meta:
        db_table = 'sub_system'

    def __str__(self):
        return str(self.name)

class Facility(models.Model):
    facility_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    short_description = models.CharField(max_length=512, blank=True, null=True)
    kks_code = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'facility'

    def __str__(self):
        return str(self.kks_code)

# to upload files in specific date
def supporting_file_upload(instance, filename):
    today = datetime.date.today()
    return os.path.join(
        'supporting_files',
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )

def mom_upload(instance, filename):
    today = datetime.date.today()
    return os.path.join(
        'MoM',
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )

class SafetyType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"

class LevelCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    event_code = models.CharField(max_length=64, blank=True, null=True)
    unit = models.CharField(max_length=16, choices=UNIT, blank=True, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.DO_NOTHING, blank=True, null=True)
    elevation = models.CharField(max_length=16, blank=True, null=True)
    room_no = models.CharField(max_length=16, blank=True, null=True)
    additional_location_info = models.CharField(max_length=128, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    event_category = models.CharField(max_length=16, choices=EVENT_CATEGORY, blank=True, null=True)
    categorical_event_code = models.CharField(max_length=64, blank=True, null=True)
    regulatory_norms_violation = models.BooleanField(blank=True, null=True, default=False)
    description = models.TextField(blank=True, null=True)
    direct_cause = models.CharField(max_length=256, blank=True, null=True)
    action_taken = models.CharField(max_length=512, blank=True, null=True)
    action_to_prevent_recurrence_event = models.CharField(max_length=512, blank=True, null=True)
    elimination_suggestion = models.CharField(max_length=512, blank=True, null=True)
    responsible_dept = models.ForeignKey(DepartmentShop, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='responsible_dept')
    plant_status = models.CharField(max_length=32, choices=PLANT_STATUS, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='uploaded_by')
    uploaded_date = models.DateField(blank=True, null=True)
    uploader_organization = models.CharField(max_length=256, blank=True, null=True)
    uploader_shop = models.ForeignKey(DepartmentShop, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='reporter_dept')
    uploader_designation = models.CharField(max_length=256, blank=True, null=True)
    uploader_phone = models.CharField(max_length=16, blank=True, null=True)
    information_source = models.CharField(max_length=16, choices=INFORMATION_SOURCE, blank=True, null=True)
    keep_identity_confidential = models.BooleanField(blank=True, null=True, default=False)
    supporting_file_1 = models.FileField(upload_to=supporting_file_upload, blank=True, null=True)
    supporting_file_2 = models.FileField(upload_to=supporting_file_upload, blank=True, null=True)
    supporting_file_3 = models.FileField(upload_to=supporting_file_upload, blank=True, null=True)
    approval_status = models.IntegerField(blank=True, null=True, default=0)
    approved_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='approved_by')
    approval_date = models.DateField(blank=True, null=True)
    updated_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='updated_by')
    updated_date = models.DateField(blank=True, null=True)
    supervisor = models.ManyToManyField(User, related_name='supervisors')
    executor = models.ManyToManyField(User, related_name='executors')
    resolution_status = models.CharField(max_length=32, choices=RESOLUTION_STATUS, blank=True, null=True)
    resolved_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='resolved_by')
    resolved_date = models.DateField(blank=True, null=True)
    resolver_remarks = models.CharField(max_length=512, blank=True, null=True)
    is_guest = models.BooleanField(blank=True, null=True, default=False)
    submission_status = models.IntegerField(blank=True, null=True)
    type_of_safety = models.ManyToManyField(SafetyType, blank=True)
    level_code = models.ManyToManyField(LevelCode, blank=True)

    # MoM for Extended Analysis of Event
    eae_mom_id = models.CharField(max_length=64, blank=True, null=True)
    eae_mom_file =  models.FileField(upload_to=mom_upload, blank=True, null=True)
    eae_mom_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'event'

    def __str__(self):
        return str(self.id)
    def supervisor_list(self):
        return list(self.supervisor.all())
    def executor_list(self):
        return list(self.executor.all())
    def expired_pending_event(self):
        return (
                    timezone.localdate() - self.uploaded_date >= datetime.timedelta(days=2)
                    and self.approval_status == 0
               )

class EventGoodPractice(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, choices=GP_NAME, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='gp_uploaded_by')
    uploaded_date = models.DateField(blank=True, null=True)
    uploader_shop = models.ForeignKey(DepartmentShop, on_delete=models.DO_NOTHING, blank=True, null=True,
                                      related_name='gp_uploader_dept')
    uploader_organization = models.CharField(max_length=256, blank=True, null=True)
    uploader_designation = models.CharField(max_length=256, blank=True, null=True)
    uploader_phone = models.CharField(max_length=16, blank=True, null=True)
    information_source = models.CharField(max_length=16, choices=INFORMATION_SOURCE, blank=True, null=True)
    log_book_no = models.CharField(max_length=128, blank=True, null=True)
    keywords = models.CharField(max_length=128, blank=True, null=True)
    reactor_type = models.CharField(max_length=128, choices=REACTOR_TYPE, blank=True, null=True)
    npp_activities = models.CharField(max_length=128, choices=NPP_ACTIVITIES, blank=True, null=True)
    main_activities = models.CharField(max_length=128, choices=MAIN_ACTIVITIES, blank=True, null=True)
    general_activities = models.CharField(max_length=128, choices=GENERAL_ACTIVITIES, blank=True, null=True)
    problem_elimination_specification = models.CharField(max_length=128, choices=GP_APPLICATION_FOR_PROBLEM_ELIMINATION, blank=True, null=True)
    gp_applications = models.CharField(max_length=128, choices=GP_APPLICATION, blank=True, null=True)
    expert_assessment = models.CharField(max_length=128, choices=EXPERT_ASSESSMENT_ON_APPLICATION, blank=True, null=True)
    distribution_recommendation = models.CharField(max_length=128, choices=GP_DISTRIBUTION_RECOMMENDATION, blank=True, null=True)
    updated_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='gp_updated_by')
    updated_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'event_good_practice'
    def __str__(self):
        return str(self.id)

class File(models.Model):
    hash = models.CharField(primary_key=True, max_length=256, null=False, blank=False)
    reference_count = models.IntegerField(blank=False, null=False, default=1)
    file_name = models.CharField(max_length=256, blank=True, null=True)
    file_type = models.CharField(max_length=20, blank=True, null=True)
    file_size = models.CharField(max_length=20, blank=True, null=True)
    server_loc = models.CharField(max_length=512, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.file_type = self.file_name.split(".")[-1]
        super(File, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Custom logic before deletion
        from event_management.ftp_handler import delete_file
        delete_file(self.server_loc)
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'files'

class GroupMsgInstruction(models.Model):
    id = models.AutoField(primary_key=True)
    send_time = models.DateTimeField(null=True)
    message_body = models.CharField(max_length=256, blank=True, null=True)
    recipients = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'group_msg_instruction'

    def __str__(self):
        return str(self.message_body)

class MsgInstructionAction(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    instruction = models.ForeignKey(GroupMsgInstruction, models.DO_NOTHING, blank=True, null=True)
    action_text = models.CharField(max_length=512, blank=True, null=True)
    file = models.ForeignKey(File, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'msg_instruction_action'