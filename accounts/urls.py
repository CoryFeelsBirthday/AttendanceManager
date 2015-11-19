from django.conf.urls import url
from .views import profile_view, add_user_view, add_user_perm_view, get_user_perm_view

urlpatterns = [
    url(r'^profile/$', profile_view, name='profile_view'),
    url(r'^add_user/$', add_user_view, name='add_user_view'),
    url(r'^get_user_permission/$', get_user_perm_view, name='get_user_perm_view'),
    url(r'^add_user_permission/$', add_user_perm_view, name='add_user_perm_view'),
]
