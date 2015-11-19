from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_text
from django import forms
from django.core.exceptions import ValidationError

# the models of record are divided into leveled model and non-leveled model
# a graph for foreign key aka many to one relation can be drew as:
#               zone
#                 |     session
#    school    program  /
#        |        |    |
#    student    schedule   --\
#         \       |           \
#          \--enrollment  canceled_data
#                 |
#               attendance    partner

class School(models.Model):
    id = models.AutoField(primary_key=True)
    school_code = models.IntegerField()
    district_id = models.IntegerField()
    name = models.CharField(max_length=50)
    address = models.TextField()

    class Meta:
        unique_together = ('district_id', 'school_code')

    def __str__(self):
        return self.name


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    local_id = models.IntegerField()
    school = models.ForeignKey(School)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    dob = models.DateField()
    gender = models.CharField(max_length=1, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('school', 'local_id')

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.school.name + ' ' + self.local_id.__str__()


class Zone(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    zone_description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    zone = models.ForeignKey(Zone)
    program_description = models.TextField(blank=True)

    class Meta:
        unique_together = ('name', 'zone')

    def __str__(self):
        return self.zone.name + ' ' + self.name


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

WEEKDAYS_CHOICES = (
    ('Mon', 'Mon'),
    ('Tue', 'Tue'),
    ('Wed', 'Wed'),
    ('Thu', 'Thu'),
    ('Fri', 'Fri'),
    ('Sat', 'Sat'),
    ('Sun', 'Sun'),
)


class MultipleWeekdaysField(models.Field):
    description = "Comma separated weekdays field"


    def get_internal_type(self):
        return 'TextField'

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return value[:-1].split(',')

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'], code='invalid_list')
        return [smart_text(val) for val in value]

    def get_prep_value(self, value):
        return ','.join(value)+','

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.MultipleChoiceField}
        kwargs['choices'] = WEEKDAYS_CHOICES
        defaults.update(kwargs)
        return super(MultipleWeekdaysField, self).formfield(**defaults)


class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    program = models.ForeignKey(Program)
    session = models.ForeignKey(Session)
    teacher = models.ForeignKey(User)
    address = models.TextField()
    # this is a field of list of available weekdays for this schedule,
    # it will be reflected in take_attendance page
    meeting_day = MultipleWeekdaysField()

    class Meta:
        unique_together = ('session', 'program')

    def __str__(self):
        return self.program.__str__() + ' ' + self.session.name


class CanceledDate(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule)
    date = models.DateField()
    comment = models.TextField(max_length=200, blank=True)

    class Meta:
        unique_together = ('schedule', 'date')

    def __str__(self):
        return self.schedule.__str__() + ' canceled at ' + self.date.__str__()


class Enrollment(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule)
    student = models.ForeignKey(Student)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        # every student only have one session a year but may have
        # multiple session schedules if he change classes
        unique_together = ('schedule', 'student')

    def __str__(self):
        return self.student.__str__() + ' in ' + self.schedule.__str__()


class Partner(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    STATUS_TYPE = (
        ('P', 'Present'),
        ('E', 'Excused'),
        ('A', 'Absent')
    )
    enrollment = models.ForeignKey(Enrollment)
    date = models.DateField()
    attendance_status = models.CharField(max_length=10, choices=STATUS_TYPE, blank=True)
    attendance_comment = models.TextField(blank=True)
    partner = models.ForeignKey(Partner, null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'date')

    def __str__(self):
        return self.enrollment.student.__str__() + ' in ' + self.enrollment.schedule.__str__() + \
            ' on date ' + self.date.__str__()
