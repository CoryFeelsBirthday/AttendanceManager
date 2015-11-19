from django.db import models
from django.contrib.auth.models import User
from records.models import Zone, Program, Schedule


class UserProfile(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, related_name="profile")
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # leveled permission
    zone_permission = models.ManyToManyField(Zone, blank=True)
    program_permission = models.ManyToManyField(Program, blank=True)
    schedule_permission = models.ManyToManyField(Schedule, blank=True)
    # non-leveled permission
    session_permission = models.BooleanField(default=False)
    school_permission = models.BooleanField(default=False)
    student_permission = models.BooleanField(default=False)
    partner_permission = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + "'s profile"


def get_user_profile(user):
    # if user's profile doesn't exist create a new one
    # this function should be used for every access to user's porfile
    profile = UserProfile.objects.get_or_create(user=user)
    return profile[0]
