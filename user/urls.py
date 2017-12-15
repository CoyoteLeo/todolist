from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, \
    password_reset_complete
from .views import Login, logout_action, ProfileView, Register, PasswordChange, PasswordReset

admin.autodiscover()

urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', logout_action, name='logout'),
    url(r'^password_change/$', PasswordChange.as_view(), name='password_change'),
    url(r'^password_reset/request/$', PasswordReset.Request.as_view(), name='password_reset_request'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordReset.Form.as_view(), name='password_reset_form'),
]
