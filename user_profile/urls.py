import user_profile
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from user_profile import views



urlpatterns = [
    url(r'^settings/$',  user_profile.views.settings, name='settings'),
    url(r'^(?P<prof_login>\w+)/$',  user_profile.views.profile, name='profile'),
    url(r'^(?P<prof_login>\w+)/get_money/$',  user_profile.views.get_money),
    url(r'^$',  user_profile.views.profile),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
