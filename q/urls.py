from django.conf.urls import url, include
from django.contrib import admin

import qworld
from qworld import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^quest/', include('qworld.urls')),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^rules/$', qworld.views.rules, name='rules'),
    url(r'^support/$', qworld.views.support, name='support'),
    url(r'^', include('loginsys.urls')),
]
