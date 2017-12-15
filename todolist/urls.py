from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from user.views import index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^/$', index, name="index"),
    url(r'^user/', include('user.urls', namespace="user", app_name='user')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # import debug_toolbar
    #
    # urlpatterns = [
    #                   url(r'^__debug__/', include(debug_toolbar.urls)),
    #               ] + urlpatterns
