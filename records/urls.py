from django.conf.urls import url, include
from .views import zone_view, program_view, schedule_view, enrollment_view, add_view, edit_view, delete_view, \
    attendance_view, canceled_date_view, school_view, session_view, student_view, others_add_view, others_delete_view, \
    others_edit_view, partner_view

enrollment_url_patterns = [
    url(r'^$', enrollment_view, {'model_name': 'enrollment'}, name='enrollment_view'),
    url(r'^add/$', add_view, {'model_name': 'enrollment'}, name='enrollment_add_view'),
    url(r'^(?P<student_id>[0-9]+)/edit/$', edit_view, {'model_name': 'enrollment'}, name='enrollment_edit_view'),
    url(r'^(?P<student_id>[0-9]+)/delete/$', delete_view, {'model_name': 'enrollment'}, name='enrollment_delete_view'),
    url(r'^(?P<date>(\d{4}-\d+-\d+))/$', attendance_view, name='attendance_view'),
]

canceled_date_url_patterns = [
    url(r'^$', canceled_date_view, {'model_name': 'canceled_date'}, name='canceled_date_view'),
    url(r'^add/$', add_view, {'model_name': 'canceled_date'}, name='canceled_date_add_view'),
    url(r'^(?P<canceled_date>([0-9\-])+)/edit/$', edit_view, {'model_name': 'canceled_date'},
        name='canceled_date_edit_view'),
    url(r'^(?P<canceled_date>([0-9\-])+)/delete/$', delete_view, {'model_name': 'canceled_date'},
        name='canceled_date_delete_view'),
]

schedule_url_patterns = [
    url(r'^$', schedule_view, {'model_name': 'schedule'}, name='schedule_view'),
    url(r'^add/$', add_view, {'model_name': 'schedule'}, name='schedule_add_view'),
    url(r'^(?P<session_name>[^/]+)/edit/$', edit_view, {'model_name': 'schedule'}, name='schedule_edit_view'),
    url(r'^(?P<session_name>[^/]+)/delete/$', delete_view, {'model_name': 'schedule'}, name='schedule_delete_view'),
    url(r'^(?P<session_name>[^/]+)/enrollments/', include(enrollment_url_patterns)),
    url(r'^(?P<session_name>[^/]+)/canceled_dates/', include(canceled_date_url_patterns)),
]
program_url_patterns = [
    url(r'^$', program_view, {'model_name': 'program'}, name='program_view'),
    url(r'^add/$', add_view, {'model_name': 'program'}, name='program_add_view'),
    url(r'^(?P<program_name>[^/]+)/edit/$', edit_view, {'model_name': 'program'}, name='program_edit_view'),
    url(r'^(?P<program_name>[^/]+)/delete/$', delete_view, {'model_name': 'program'}, name='program_delete_view'),
    url(r'^(?P<program_name>[^/]+)/schedules/', include(schedule_url_patterns)),
]
zone_url_patterns = [
    url(r'^$', zone_view, {'model_name': 'zone'}, name='zone_view'),
    url(r'^add/$', add_view, {'model_name': 'zone'}, name='zone_add_view'),
    url(r'^(?P<zone_name>[^/]+)/edit/$', edit_view, {'model_name': 'zone'}, name='zone_edit_view'),
    url(r'^(?P<zone_name>[^/]+)/delete/$', delete_view, {'model_name': 'zone'}, name='zone_delete_view'),
    url(r'^(?P<zone_name>[^/]+)/programs/', include(program_url_patterns)),
]
student_url_patterns = [
    url(r'^$', student_view, {'model_name': 'student'}, name='student_view'),
    url(r'^add/$', others_add_view, {'model_name': 'student'}, name='student_add_view'),
    url(r'^(?P<id>[^/]+)/edit/$', others_edit_view, {'model_name': 'student'}, name='student_add_view'),
    url(r'^(?P<id>[^/]+)/delete/$', others_delete_view, {'model_name': 'student'}, name='student_delete_view'),
]
school_url_patterns = [
    url(r'^$', school_view, {'model_name': 'school'}, name='school_view'),
    url(r'^add/$', others_add_view, {'model_name': 'school'}, name='school_add_view'),
    url(r'^(?P<id>[^/]+)/edit/$', others_edit_view, {'model_name': 'school'}, name='school_add_view'),
    url(r'^(?P<id>[^/]+)/delete/$', others_delete_view, {'model_name': 'school'}, name='school_delete_view'),
]
session_url_patterns = [
    url(r'^$', session_view, {'model_name': 'session'}, name='session_view'),
    url(r'^add/$', others_add_view, {'model_name': 'session'}, name='session_add_view'),
    url(r'^(?P<id>[^/]+)/edit/$', others_edit_view, {'model_name': 'session'}, name='session_add_view'),
    url(r'^(?P<id>[^/]+)/delete/$', others_delete_view, {'model_name': 'session'}, name='session_delete_view'),
]
partner_url_patterns = [
    url(r'^$', partner_view, {'model_name': 'partner'}, name='partner_view'),
    url(r'^add/$', others_add_view, {'model_name': 'partner'}, name='partner_add_view'),
    url(r'^(?P<id>[^/]+)/edit/$', others_edit_view, {'model_name': 'partner'}, name='partner_add_view'),
    url(r'^(?P<id>[^/]+)/delete/$', others_delete_view, {'model_name': 'partner'}, name='partner_delete_view'),
]
urlpatterns = [
    url(r'^zones/', include(zone_url_patterns)),
    url(r'^schools/', include(school_url_patterns)),
    url(r'^sessions/', include(session_url_patterns)),
    url(r'^students/', include(student_url_patterns)),
    url(r'^partners/', include(partner_url_patterns))
]
