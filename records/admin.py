from django.contrib import admin
from records.models import School, Student, Zone, Program, Session, Schedule, \
    Partner, CanceledDate, Enrollment, Attendance

admin.site.register(School)
admin.site.register(Student)
admin.site.register(Zone)
admin.site.register(Program)
admin.site.register(Session)
admin.site.register(Schedule)
admin.site.register(Partner)
admin.site.register(CanceledDate)
admin.site.register(Enrollment)
admin.site.register(Attendance)
