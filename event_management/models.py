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

INFORMATION_SOURCE = (
    ("", "-------"),
    ("internal", "Internal"),
    ("external", "External"),
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
def file_upload_to_folder(instance, filename):
    today = datetime.date.today()
    return os.path.join(
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    unit = models.CharField(max_length=16, choices=UNIT, blank=True, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.DO_NOTHING, blank=True, null=True)
    elevation = models.CharField(max_length=16, blank=True, null=True)
    room_no = models.CharField(max_length=16, blank=True, null=True)
    additional_location_info = models.CharField(max_length=128, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    event_category = models.CharField(max_length=64, blank=True, null=True)
    safety_importance = models.BooleanField(blank=True, null=True, default=False)
    comment_if_safety_importance = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    direct_cause = models.CharField(max_length=256, blank=True, null=True)
    action_taken = models.BooleanField(blank=True, null=True, default=False)
    comment_if_action_taken = models.CharField(max_length=256, blank=True, null=True)
    elimination_suggestion = models.CharField(max_length=256, blank=True, null=True)
    responsible_dept = models.ForeignKey(DepartmentShop, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='responsible_dept')
    plant_status = models.CharField(max_length=256, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='uploaded_by')
    uploaded_date = models.DateField(blank=True, null=True)
    uploader_shop = models.ForeignKey(DepartmentShop, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='reporter_dept')
    uploader_organization = models.CharField(max_length=256, blank=True, null=True)
    uploader_designation = models.CharField(max_length=256, blank=True, null=True)
    uploader_phone = models.CharField(max_length=16, blank=True, null=True)
    uploader_bioID = models.CharField(max_length=16, blank=True, null=True)
    information_source = models.CharField(max_length=16, choices=INFORMATION_SOURCE, blank=True, null=True)
    keep_identity_confidential = models.BooleanField(blank=True, null=True, default=False)
    supporting_file_1 = models.FileField(upload_to=file_upload_to_folder, blank=True, null=True)
    supporting_file_2 = models.FileField(upload_to=file_upload_to_folder, blank=True, null=True)
    supporting_file_3 = models.FileField(upload_to=file_upload_to_folder, blank=True, null=True)

    class Meta:
        db_table = 'event'

    def __str__(self):
        return self.description

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