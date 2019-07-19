from django.conf.urls import url
import qworld
from qworld import views
import payment_tranch
from payment_tranch import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'found/$', qworld.views.found, name='found'),
    url(r'change/(?P<quest_id>[0-9]+)/$', qworld.views.change, name='change'),
    url(r'payment/(?P<quest_id>[0-9]+)/$', payment_tranch.views.payment, name='payment'),
    url(r'payment/(?P<quest_id>[0-9]+)/pay/$', payment_tranch.views.pay),
    url(r'payment/y_success/$', payment_tranch.views.y_success),
    url(r'participate_group/(?P<quest_id>[0-9]+)/(?P<group_id>[0-9]+)/$', qworld.views.participate_group,
        name='participate_group'),
    url(r'participate/(?P<quest_id>[0-9]+)/$', qworld.views.participate,
        name='participate'),
    url(r'participate/(?P<quest_id>[0-9]+)/pay/$', payment_tranch.views.part_pay),
    url(r'participate_group/(?P<quest_id>[0-9]+)/(?P<group_id>[0-9]+)/pay/$', payment_tranch.views.part_pay),
    url(r'questend/(?P<quest_id>[0-9]+)/$', qworld.views.end,
        name='end'),
    url(r'questend/(?P<quest_id>[0-9]+)/(?P<group_id>[0-9]+)/$', qworld.views.group_end,
        name='group_end'),
    url(r'participate_group/(?P<quest_id>[0-9]+)/$', qworld.views.participate_group),
    url(r'payment/checkcode/$', payment_tranch.views.checkcode),
    url(r'group_log_in/$', qworld.views.group_log_in),
    url(r'create/$', qworld.views.create, name='create'),
    url(r'(?P<quest_id>[0-9]+)/$', qworld.views.quest, name='quest'),
    url(r'^$', qworld.views.found),
    url(r'found/get_filter_quests/$', qworld.views.get_filter_quests),
    url(r'create/get_html_groups/$', qworld.views.get_html_groups),
    url(r'create/get_html_group_waypoint/$', qworld.views.get_html_group_waypoint),
    url(r'(?P<quest_id>[0-9]+)/get_html_checkbox_photo/$', qworld.views.get_html_checkbox_photo),
    url(r'(?P<quest_id>[0-9]+)/get_html_normal_photo/$', qworld.views.get_html_normal_photo),
    url(r'(?P<quest_id>[0-9]+)/save_quest_photos/$', qworld.views.save_quest_photos),
]