import loginsys
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from loginsys import views


urlpatterns = [
    url(r'^login/$', loginsys.views.login, name='login'),
    url(r'^logout/$', loginsys.views.logout, name='logout'),
    url(r'^reminde/$', loginsys.views.reminde, name='reminde'),
    url(r'^reminde_confirmation/$', loginsys.views.reminde_confirmation),
    url(r'^registration/$', loginsys.views.registration, name='registration'),
    url(r'^$', loginsys.views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
