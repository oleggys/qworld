import datetime
import os
import random
import pytz
import requests
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib import auth
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

from payment_tranch.models import Part_Order
from q.settings import MEDIA_ROOT, EMAIL_HOST_USER
from qworld.forms import CreateQuestForm, SupportMessageForm
from qworld.models import Quest, Player, Quest_Group, Group_Player, Category, Waypoint, Questions, Photo
from django.utils import timezone
from user_profile.models import Created_quest, Waiting_quest, Participated_quest, ExtUser, Achievement_user, Achievement
from django.template.loader import get_template
from django.template import Context


def randomcolor():
    return ''.join([random.choice(list('0123456789ADFCB')) for x in range(6)])


def found(request):
    args = {}
    if request.user.is_authenticated():
        args['auth_user'] = auth.get_user(request)
        args['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        quests = Quest.objects.all().filter(mon_paid=True).order_by('-creation_time')
        paginator = Paginator(quests, 12)
        page = request.GET.get('page')
        try:
            quests = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            quests = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            quests = paginator.page(paginator.num_pages)
        args['quests'] = quests
        categories = Category.objects.all()
        categ = {}
        categ_number = 0
        for category in categories:
            categ_number += category.id
            categ.update({categ_number: category})
        args['categories'] = categ
        return render(request, 'qworld/found.html', args)
    else:
        return redirect('/')


def change(request, quest_id=0):
    if request.user.is_authenticated():
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        auth_user = auth.get_user(request)
        args['auth_user'] = auth_user
        obj_quest = get_object_or_404(Quest, id=quest_id, mon_paid=True)
        args['quest'] = obj_quest
        if obj_quest.begin_date_time > Now:
            if int(obj_quest.author_id) == auth.get_user(request).id:
                # ----------------------------------------------------
                if request.POST:
                    change_form = CreateQuestForm(request.POST, request.FILES)
                    if obj_quest.avatar:
                        change_form.avatar = obj_quest.avatar.url
                    k = 0
                    agree_k = 0
                    if request.POST.get('have_group'):
                        group_waypoints = {}
                        group_waypoints.update({1: ['', '', '', '', {1: ['', '', '', '', '', False]}]})
                        group_waypoints.update({2: ['', '', '', '', {1: ['', '', '', '', '', False]}]})
                        args['group_waypoints'] = group_waypoints
                        len_group = request.POST.getlist('group_color')
                        agree_g = 0
                        for i in range(1, len(len_group) + 1):
                            col = 0
                            color = len_group[i - 1]
                            group_name = request.POST.get('q_group_name-' + str(i))
                            if not (str(group_name).isspace() or group_name is None or group_name is ''):
                                agree_g += 1
                                admin_log = request.POST.get('q_admin_log-' + str(i))
                                admin_pas = request.POST.get('q_admin_password-' + str(i))
                                waypoints = {}
                                waypoints.update({1: ['', '', '', '', '', False]})
                                len_way_groups = len(request.POST.getlist('q-col-' + str(i)))
                                for j in range(1, len_way_groups + 1):
                                    address = request.POST.get('q_address-' + str(i) + '-' + str(j))
                                    sh = request.POST.get('sh-' + str(i) + '-' + str(j))[0:9]
                                    dl = request.POST.get('dl-' + str(i) + '-' + str(j))[0:9]
                                    secret_key = request.POST.get('q_code-' + str(i) + '-' + str(j))
                                    desc = request.POST.get('q_description-' + str(i) + '-' + str(j))
                                    if not (str(address).isspace() or address is None or address is ''):
                                        k += 1
                                        col += 1
                                        if dl is '' or sh is '':
                                            agree = False
                                        else:
                                            agree = True
                                            agree_k += 1
                                        waypoints.update({col: [address, sh, dl, secret_key, desc, agree]})
                                group_waypoints.update({agree_g: [color, group_name, admin_log, admin_pas, waypoints]})
                        args['group_waypoints'] = group_waypoints
                    else:
                        waypoints = {}
                        waypoints.update({1: ['', '', '', '', '', False]})
                        agree = False
                        ways = len(request.POST.getlist('q-col'))
                        for i in range(1, ways + 1):
                            address = request.POST.get('q_address-' + str(i))
                            sh = request.POST.get('sh-' + str(i))[0:9]
                            dl = request.POST.get('dl-' + str(i))[0:9]
                            secret_key = request.POST.get('q_code-' + str(i))
                            desc = request.POST.get('q_description-' + str(i))
                            if not (str(address).isspace() or address is None or address is ''):
                                k += 1
                                if dl is '' or sh is '':
                                    agree = False
                                else:
                                    agree = True
                                    agree_k += 1
                                waypoints.update({k: [address, sh, dl, secret_key, desc, agree]})
                        args['waypoints'] = waypoints
                    if change_form.is_valid() and agree_k == k:
                        m_q = []
                        for group in Quest_Group.objects.all().filter(for_quest=obj_quest):
                            m_q.append(group.id)
                        change_form.category = change_form.cleaned_data['category']
                        if change_form.cleaned_data['avatar']:
                            obj_quest.avatar = change_form.cleaned_data['avatar']
                        obj_quest.name = change_form.cleaned_data['name']
                        obj_quest.target = change_form.cleaned_data['target']
                        obj_quest.description = change_form.cleaned_data['description']
                        if change_form.cleaned_data['password'] != '' and not change_form.cleaned_data['password'].isspace():
                            obj_quest.password = change_form.cleaned_data['password']
                        obj_quest.have_password = change_form.cleaned_data['have_password']
                        obj_quest.have_group = change_form.cleaned_data['have_group']
                        obj_quest.paid = change_form.cleaned_data['paid']
                        obj_quest.cost = change_form.cleaned_data['cost']
                        obj_quest.category = change_form.cleaned_data['category']
                        obj_quest.town = change_form.cleaned_data['town']
                        obj_quest.meeting_point = change_form.cleaned_data['meeting_point']
                        obj_quest.meeting_date_time = change_form.cleaned_data['meeting_date_time']
                        obj_quest.begin_date_time = change_form.cleaned_data['begin_date_time']
                        obj_quest.end_date_time = change_form.cleaned_data['end_date_time']
                        obj_quest.save()
                        if request.POST.get('have_group'):
                            for group_id in group_waypoints:
                                try:
                                    if group_waypoints[group_id][1] != '':
                                        group = Quest_Group(id=m_q[group_id - 1])
                                        group.name = group_waypoints[group_id][1]
                                        group.admin_login = group_waypoints[group_id][2]
                                        group.admin_password = group_waypoints[group_id][3]
                                        group.for_quest = obj_quest
                                        group.save()
                                        waypoints = group_waypoints[group_id][4]
                                        m_w = []
                                        for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest,
                                                                                      for_gid=group.id):
                                            m_w.append(waypoint.id)
                                        for key in waypoints:
                                            try:
                                                wayp = Waypoint(id=m_w[key-1])
                                                wayp.address_s = waypoints[key][1]
                                                wayp.address_d = waypoints[key][2]
                                                wayp.tip = waypoints[key][4]
                                                wayp.for_gid = m_q[group_id-1]
                                                wayp.code = waypoints[key][3]
                                                wayp.for_quest = obj_quest
                                                wayp.save()
                                            except Exception as err:
                                                wayp = Waypoint(address_s=waypoints[key][1],
                                                                address_d=waypoints[key][2],
                                                                tip=waypoints[key][4], for_gid=m_q[group_id-1],
                                                                code=waypoints[key][3],
                                                                for_quest=obj_quest)
                                                wayp.save()
                                    else:
                                        try:
                                            gr = Quest_Group(id=m_q[group_id - 1])
                                            Group_Player.objects.all().filter(for_group=gr).delete()
                                            gr.delete()
                                            Waypoint.objects.all().filter(for_gid=m_q[group_id - 1]).delete()
                                        except Exception as err:
                                            pass
                                except Exception as err:
                                    group = Quest_Group(name=group_waypoints[group_id][1],
                                                        admin_login=group_waypoints[group_id][2],
                                                        admin_password=group_waypoints[group_id][3],
                                                        for_quest=obj_quest)
                                    group.save()
                                    waypoints = group_waypoints[group_id][4]
                                    for key in waypoints:
                                        wayp = Waypoint(address_s=waypoints[key][1], address_d=waypoints[key][2],
                                                        tip=waypoints[key][4], for_gid=group.id, code=waypoints[key][3],
                                                        for_quest=obj_quest)
                                        wayp.save()
                        else:
                            m_w = []
                            agree_ids = []
                            for group in Quest_Group.objects.all().filter(for_quest=obj_quest):
                                Group_Player.objects.all().filter(for_group=group).delete()
                            Quest_Group.objects.all().filter(for_quest=obj_quest).delete()
                            for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest):
                                m_w.append(waypoint.id)
                            for key in waypoints:
                                try:
                                    wayp = Waypoint.objects.get(id=m_w[key-1])
                                    wayp.address_s = waypoints[key][1]
                                    wayp.address_d = waypoints[key][2]
                                    wayp.tip = waypoints[key][4]
                                    wayp.code = waypoints[key][3]
                                    wayp.for_quest = obj_quest
                                    wayp.save()
                                    agree_ids.append(m_w[key-1])
                                except Exception as err:
                                    wayp = Waypoint(address_s=waypoints[key][1], address_d=waypoints[key][2],
                                                    tip=waypoints[key][4], code=waypoints[key][3],
                                                    for_quest=obj_quest)
                                    wayp.save()
                            if len(waypoints) < len(Waypoint.objects.all().filter(for_quest=obj_quest)):
                                for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest):
                                    if waypoint.id not in agree_ids:
                                        waypoint.delete()
                        attr = {}
                        attr['auth_user'] = auth.get_user(request)
                        attr['quest'] = Quest.objects.get(id=quest_id)
                        to = auth.get_user(request).email
                        subject, from_email = 'Внесены изменения в квест', EMAIL_HOST_USER
                        html_content = get_template('email/change_quest.html').render(Context(attr))
                        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return redirect('quest', quest_id)
                    else:
                        args['CreateQuestForm'] = CreateQuestForm(request.POST, request.FILES)
                        return render(request, 'qworld/quest_change.html', args)
                # ----------------------------------------------------
                else:
                    categories = list()
                    for category in obj_quest.category.all():
                        categories.append(category.id)
                    args['quest'] = obj_quest
                    data = {'name': obj_quest.name, 'password': obj_quest.password,
                            'target': obj_quest.target, 'description': obj_quest.description,
                            'have_password': obj_quest.have_password, 'have_group': obj_quest.have_group,
                            'paid': obj_quest.paid, 'cost': obj_quest.cost, 'town': obj_quest.town,
                            'begin_date_time': obj_quest.begin_date_time, 'end_date_time': obj_quest.end_date_time,
                            'meeting_point': obj_quest.meeting_point, 'meeting_date_time': obj_quest.meeting_date_time,
                            'category': categories}
                    if obj_quest.have_group:
                        k = 0
                        group_waypoints = {}
                        for group in Quest_Group.objects.all().filter(for_quest=obj_quest):
                            k += 1
                            waypoints = {}
                            j = 0
                            for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest, for_gid=group.id):
                                j += 1
                                waypoints.update({j: ['', waypoint.address_s, waypoint.address_d, waypoint.code,
                                                      waypoint.tip, True]})
                            group_waypoints.update({k: [randomcolor(), group.name, group.admin_login, group.admin_password,
                                                        waypoints]})
                        if k % 2 != 0:
                            group_waypoints.update({k+1: [randomcolor(), '', '', '', {1: ['', '', '', '', '', False]}]})
                        args['group_waypoints'] = group_waypoints
                    else:
                        l = 0
                        waypoints = {}
                        for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest):
                            l += 1
                            waypoints.update({l: ['', waypoint.address_s, waypoint.address_d, waypoint.code,
                                                      waypoint.tip, True]})
                            args['waypoints'] = waypoints
                    args['CreateQuestForm'] = CreateQuestForm(initial=data)
                    return render(request, 'qworld/quest_change.html', args)
            else:
                return redirect('quest', quest_id)
        else:
            return redirect('quest', quest_id)
    else:
        return redirect('/')


def quest(request, quest_id=0):
    args = {}
    Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    if request.user.is_authenticated():
        auth_user = auth.get_user(request)
        args['auth_user'] = auth_user
        try:
            obj_quest = Quest.objects.get(id=quest_id, mon_paid=True)
        except Exception as err:
            return render(request, 'qworld/quest_dont_exist.html', args)
        if obj_quest.begin_date_time > Now:  # квест ещё не начался
            list_of_players = []
            try:
                players = Player.objects.all().filter(for_quest=obj_quest)
                for player in players:
                    list_of_players.append(player.player_id)
            except Exception as err:
                list_of_players = []
            args['part_yet'] = False
            if auth_user.id in list_of_players:
                args['part_yet'] = True
            # можете принять участие
            args['quest'] = obj_quest
            if obj_quest.have_group:
                list_of_group = Quest_Group.objects.all().filter(for_quest=obj_quest)
                list_of_group_player = []
                len_group_players = 0
                for group in list_of_group:
                    try:
                        for group_player in Group_Player.objects.all().filter(for_group=group):
                            list_of_group_player.append(group_player.player_id)
                            len_group_players += 1
                    except Exception as err:
                        list_of_group_player = []
                    group.len_group_players = len_group_players
                    len_group_players = 0
                args['groups'] = list_of_group
                return render(request, 'qworld/quest_participate.html', args)
            else:
                return render(request, 'qworld/quest_participate.html', args)  # принять участие для одного
        elif obj_quest.begin_date_time <= Now and Now <= obj_quest.end_date_time:  # квест идёт
            if obj_quest.author_id == auth.get_user(request).id:
                # вы не можете изменять квест во время того как он идёт
                args['quest'] = obj_quest
                return render(request, 'qworld/quest_cant_change.html', args)
            else:
                list_of_players = []
                try:
                    players = Player.objects.all().filter(for_quest=obj_quest)
                    for player in players:
                        list_of_players.append(player.player_id)
                except Exception as err:
                    list_of_players = []
                if auth_user.id in list_of_players:
                    # участие для одного!
                    args['quest'] = obj_quest
                    if obj_quest.have_group:
                        # участие в группе
                        return render(request, 'qworld/quest_is_going_for_group.html', args)
                    else:
                        # участие для одного
                        cords = []
                        player = Player.objects.get(for_quest=obj_quest, player_id=auth.get_user(request).id)
                        args['result'] = player.completed_percent
                        args['completed'] = player.completed
                        waypoints = Waypoint.objects.all().filter(for_quest=obj_quest)
                        for waypoint in waypoints:
                            waypoint.code = ''
                            cords.append([float(waypoint.address_d), float(waypoint.address_s)])
                        args['waypoints'] = waypoints
                        args['cords'] = cords
                        return render(request, 'qworld/quest_is_going.html', args)
                else:
                    args['quest'] = obj_quest
                    # ждите конца
                    return render(request, 'qworld/quest_wait_end.html', args)
        else:  # квест закончился
            patency = 0.0
            k = 0
            players = {}
            for player in Player.objects.all().filter(for_quest=obj_quest):
                patency += player.completed_percent
                k += 1
                player.key = k
                players.update({player: ExtUser.objects.get(id=player.player_id)})
            if k != 0:
                patency = int(patency / k)
            else:
                patency = 0
            obj_quest.patency = patency
            args['quest'] = obj_quest
            args['players'] = players
            waypoints = Waypoint.objects.all().filter(for_quest=obj_quest)
            if obj_quest.have_group:
                cords = {}
                groups = Quest_Group.objects.all().filter(for_quest=obj_quest)
                k = 0
                for group in groups:
                    group.key = k
                    waypoints = Waypoint.objects.all().filter(for_quest=obj_quest, for_gid=group.id)
                    group_cords = []
                    for waypoint in waypoints:
                        group_cords.append([float(waypoint.address_d), float(waypoint.address_s)])
                    cords.update({k: group_cords})
                    k += 1
                args['groups'] = groups
                quest_players = {}
                for group in groups:
                    for player in Group_Player.objects.all().filter(for_group=group):
                        player.key = group.id
                        pl_user = ExtUser.objects.get(id=player.player_id)
                        quest_players.update({player: pl_user})
                args['quest_players'] = quest_players
            else:
                cords = []
                for waypoint in waypoints:
                    cords.append([float(waypoint.address_d), float(waypoint.address_s)])
            args['cords'] = cords
            args['waypoints'] = Waypoint.objects.all().filter(for_quest=obj_quest)
            photos = []
            k = 0
            for photo in Photo.objects.all().filter(for_quest=obj_quest):
                k += 1
                photo.key = k
                photos.append(photo)
            args['photos'] = photos
            return render(request, 'qworld/quest_end.html', args)
    else:
        return redirect('/')


@csrf_protect
def create(request):
    args = {}
    if request.user.is_authenticated():
        args['auth_user'] = auth.get_user(request)
        args['CreateQuestForm'] = CreateQuestForm(request.POST or None)
        waypoints = {}
        group_waypoints = {}
        if request.POST:
            payload = {'secret': '6LeUTSsUAAAAACuIG4UccPsZ7eiBman2usBEGXv3',
                       'response': str(request.POST['g-recaptcha-response'])}
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
            is_user = r.text.replace("{", "").replace("}", "").split(",")[0].split(":")[1]
            if is_user.replace(" ","") == 'true':
                create_form = CreateQuestForm(request.POST, request.FILES)
                k = 0
                agree_k = 0
                if request.POST.get('have_group'):
                    group_waypoints = {}
                    group_waypoints.update({1: ['', '', '', '', {1: ['', '', '', '', '', False]}]})
                    group_waypoints.update({2: ['', '', '', '', {1: ['', '', '', '', '', False]}]})
                    args['group_waypoints'] = group_waypoints
                    len_group = request.POST.getlist('group_color')
                    agree_g = 0
                    for i in range(1, len(len_group) + 1):
                        col = 0
                        color = len_group[i-1]
                        group_name = request.POST.get('q_group_name-' + str(i))
                        if not (str(group_name).isspace() or group_name is None or group_name is ''):
                            agree_g += 1
                            admin_log = request.POST.get('q_admin_log-' + str(i))
                            admin_pas = request.POST.get('q_admin_password-' + str(i))
                            waypoints = {}
                            waypoints.update({1: ['', '', '', '', '', False]})
                            len_way_groups = len(request.POST.getlist('q-col-' + str(i)))
                            for j in range(1, len_way_groups + 1):
                                address = request.POST.get('q_address-' + str(i) + '-' + str(j))
                                sh = request.POST.get('sh-' + str(i) + '-' + str(j))[0:9]
                                dl = request.POST.get('dl-' + str(i) + '-' + str(j))[0:9]
                                secret_key = request.POST.get('q_code-' + str(i) + '-' + str(j))
                                desc = request.POST.get('q_description-' + str(i) + '-' + str(j))
                                if not (str(address).isspace() or address is None or address is ''):
                                    k += 1
                                    col += 1
                                    if dl is '' or sh is '':
                                        agree = False
                                    else:
                                        agree = True
                                        agree_k += 1
                                    waypoints.update({col: [address, sh, dl, secret_key, desc, agree]})
                            group_waypoints.update({agree_g: [color, group_name, admin_log, admin_pas, waypoints]})
                    args['group_waypoints'] = group_waypoints
                else:
                    waypoints = {}
                    waypoints.update({1: ['', '', '', '', '', False]})
                    agree = False
                    ways = len(request.POST.getlist('q-col'))
                    for i in range(1, ways + 1):
                        address = request.POST.get('q_address-' + str(i))
                        sh = request.POST.get('sh-' + str(i))[0:9]
                        dl = request.POST.get('dl-' + str(i))[0:9]
                        secret_key = request.POST.get('q_code-' + str(i))
                        desc = request.POST.get('q_description-' + str(i))
                        if not (str(address).isspace() or address is None or address is ''):
                            k += 1
                            if dl is '' or sh is '':
                                agree = False
                            else:
                                agree = True
                                agree_k += 1
                            waypoints.update({k: [address, sh, dl, secret_key, desc, agree]})
                    args['waypoints'] = waypoints
                if create_form.is_valid() and agree_k == k:
                    create_form.author_id = auth.get_user(request).id
                    create_form.category = create_form.cleaned_data['category']
                    quest_obj_id = create_form.save()
                    quest_obj = Quest.objects.get(id=quest_obj_id)
                    if request.POST.get('have_group'):
                        for group_id in group_waypoints:
                            group = Quest_Group(name=group_waypoints[group_id][1],
                                                admin_login=group_waypoints[group_id][2],
                                                admin_password=group_waypoints[group_id][3],
                                                for_quest=quest_obj)
                            group.save()
                            waypoints = group_waypoints[group_id][4]
                            for key in waypoints:
                                wayp = Waypoint(address_s=waypoints[key][1], address_d=waypoints[key][2],
                                                tip=waypoints[key][4], for_gid=group.id, code=waypoints[key][3],
                                                for_quest=quest_obj)
                                wayp.save()
                    else:
                        for key in waypoints:
                            wayp = Waypoint(address_s=waypoints[key][1], address_d=waypoints[key][2],
                                            tip=waypoints[key][4], code=waypoints[key][3],
                                            for_quest=quest_obj)
                            wayp.save()
                    created_quest = Waiting_quest(quest_id=quest_obj_id, for_user=auth.get_user(request))
                    created_quest.save()
                    attr = {}
                    attr['auth_user'] = auth.get_user(request)
                    attr['quest'] = Quest.objects.get(id=quest_obj_id)
                    to = auth.get_user(request).email
                    subject, from_email = 'Создание квеста', EMAIL_HOST_USER
                    html_content = get_template('email/create_quest.html').render(Context(attr))
                    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return redirect('payment', quest_obj_id)
                else:
                    args['CreateQuestForm'] = CreateQuestForm(request.POST, request.FILES)
                    args['have_group'] = request.POST.get('have_group')
                    return render(request, 'qworld/create.html', args)
            else:
                return redirect('create')
        else:
            return render(request, 'qworld/create.html', args)
    else:
        return redirect('/')

@csrf_protect
def get_filter_quests(request):
    if request.GET:
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        args['now'] = datetime.datetime.now()
        name = request.GET['name']
        town = request.GET['town']
        categories = request.GET['categories'].split("|")
        have_group = request.GET['have_group']
        have_password = request.GET['have_password']
        begin_date = request.GET['begin_date']
        b_date = begin_date.split('.')
        end_date = request.GET['end_date']
        e_date = end_date.split('.')
        status = int(request.GET['status'])
        pay_status = request.GET['pay_status']
        min_cost = request.GET['min_pay']
        max_cost = request.GET['max_pay']
        quests = Quest.objects.all().filter(mon_paid=True)
        if name != '':
            quests = quests.filter(name__contains=name)
        if town != '':
            quests = quests.filter(town__contains=town)
        if have_group == 'True':
            quests = quests.filter(have_group=True)
        if have_group == 'False':
            quests = quests.filter(have_group=False)
        if have_password == 'true':
            quests = quests.filter(have_password=True)
        if have_password == 'false':
            quests = quests.filter(have_password=False)
        if pay_status == 'True':
            quests = quests.filter(paid=True)
            quests = quests.filter(cost__gte=min_cost)
            quests = quests.filter(cost__lte=max_cost)
        if pay_status == 'False':
            quests = quests.filter(paid=False)
        if begin_date != '':
            quests = quests.filter(creation_time__date__gte=datetime.date(int(b_date[2]), int(b_date[1]), int(b_date[0])))
        if end_date != '':
            quests = quests.filter(end_date_time__date__lte=datetime.date(int(e_date[2]), int(e_date[1]), int(e_date[0])))
        if not categories == ['']:
            quests = quests.filter(category__name__in=categories)
        if status == 1:
            quests = quests.filter(begin_date_time__gt=Now)
        if status == 2:
            quests = quests.filter(begin_date_time__lte=Now)
            quests = quests.filter(end_date_time__gte=Now)
        if status == 3:
            quests = quests.filter(end_date_time__lt=Now)
        quests = quests.order_by('-creation_time')
        paginator = Paginator(quests, 12)
        page = request.GET.get('page')
        try:
            quests = paginator.page(page)
        except PageNotAnInteger:
            quests = paginator.page(1)
        except EmptyPage:
            quests = paginator.page(paginator.num_pages)
        args['quests'] = quests
        args['cat'] = categories
        return render_to_response('qworld/filter_quests.html', args)


@csrf_exempt
def get_html_groups(request):
    if request.method == 'POST':
        option = int(request.POST['option'])
        if option == 2:
            args = {}
            random_color_1 = ''.join([random.choice(list('0123456789ADFCB')) for x in range(6)])
            args['random_color_1'] = random_color_1
            random_color_2 = ''.join([random.choice(list('0123456789ADFCB')) for x in range(6)])
            args['random_color_2'] = random_color_2
            args['id_2'] = int(request.POST['gid'])
            args['id_1'] = int(request.POST['gid']) - 1
            return render_to_response('qworld/requests/groups.html', args)
        elif option == 1:
            args = {}
            args['id'] = request.POST['oid']
            return render_to_response('qworld/requests/only.html', args)


@csrf_exempt
def get_html_group_waypoint(request):
    if request.method == 'POST':
        args = {}
        args['group_id'] = request.POST['group_id']
        args['waypoint_id'] = request.POST['group_waypoint_id']
        return render_to_response('qworld/requests/group_waypoint.html', args)


def rules(request):
    if request.user.is_authenticated():
        args = {}
        args['auth_user'] = auth.get_user(request)
        questions = Questions.objects.all()
        args['questions'] = questions
        return render_to_response('rules/rules.html', args)
    else:
        return redirect('/')


@csrf_exempt
def participate_group(request, quest_id=0, group_id=None):
    if request.user.is_authenticated():
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        args.update(csrf(request))
        quest_obj = get_object_or_404(Quest, id=quest_id)
        if request.method == 'POST':
            try:
                password = request.POST['part_password']
            except Exception as err:
                password = ''
            if quest_obj.password == password:

                if quest_obj.have_group and group_id is not None:
                    list_of_players = []
                    try:
                        players = Player.objects.all().filter(for_quest=quest_obj)
                        for player in players:
                            list_of_players.append(player.player_id)
                    except Exception as err:
                        list_of_players = []
                    if quest_obj.author_id != auth.get_user(request).id and not auth.get_user(request).id in list_of_players:
                        if quest_obj.paid:
                            # есть плата за цчастие
                            args['auth_user'] = auth.get_user(request)
                            args['quest'] = quest_obj
                            args['now'] = Now
                            try:
                                pay_number = str(Part_Order.objects.get(quest_id=quest_id,
                                                                        user_id=auth.get_user(request).id).uuid)[1::]
                            except Exception as err:
                                pay_number = ''.join([random.choice(list('0123456789ADFCB')) for x in range(12)])
                            args['pay_number'] = pay_number
                            return render(request, 'qworld/requests/part_pay_form.html', args)
                        else:
                            # нет платы за участие
                            group_obj = Quest_Group.objects.get(for_quest=quest_obj, id=group_id)
                            group_player = Group_Player(for_group=group_obj, player_id=auth.get_user(request).id)
                            group_player.save()
                            quest_obj.participants += 1
                            quest_obj.save()
                            player = Player(player_id=auth.get_user(request).id, completed_percent=0, for_quest=quest_obj)
                            player.save()
                            user = ExtUser.objects.get(id=auth.get_user(request).id)
                            user.level_points += 140
                            if user.level_points >= 1000:
                                user.level_points -= 1000
                                user.level += 1
                            user.save()
                            participated_quest = Participated_quest(quest_id=quest_id, for_user=auth.get_user(request))
                            participated_quest.save()
                            args['quest'] = quest_obj
                            args['auth_user'] = auth.get_user(request)
                            attr = {}
                            attr['auth_user'] = auth.get_user(request)
                            attr['quest'] = quest_obj 
                            to = auth.get_user(request).email
                            subject, from_email = 'Уведомление об участии в квесте', EMAIL_HOST_USER
                            html_content = get_template('email/participate.html').render(Context(attr))
                            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            return render(request, 'qworld/quest_wait_of_begin.html', args)
                    else:
                        # вы уже участвовуете
                        return redirect('quest', quest_id)
                else:
                    # не пытайтесь поставить свои правила
                    return redirect('found')
            else:
                args['password_err'] = True
                args['quest'] = quest_obj
                args['auth_user'] = auth.get_user(request)
                list_of_group = Quest_Group.objects.all().filter(for_quest=quest_obj)
                list_of_group_player = []
                len_group_players = 0
                for group in list_of_group:
                    try:
                        for group_player in Group_Player.objects.all().filter(for_group=group):
                            list_of_group_player.append(group_player.player_id)
                            len_group_players += 1
                    except Exception as err:
                        list_of_group_player = []
                    group.len_group_players = len_group_players
                    len_group_players = 0
                args['groups'] = list_of_group
                return render(request, 'qworld/quest_participate.html', args)
    else:
        return redirect('/')


@csrf_exempt
def participate(request, quest_id=0):
    if request.user.is_authenticated():
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        quest_obj = get_object_or_404(Quest, id=quest_id)
        if request.method == 'POST':
            try:
                password = request.POST['part_password']
            except Exception as err:
                password = ''
            if quest_obj.password == password:
                if quest_obj.have_group is False:
                    list_of_players = []
                    try:
                        players = Player.objects.all().filter(for_quest=quest_obj)
                        for player in players:
                            list_of_players.append(player.player_id)
                    except Exception as err:
                        list_of_players = []
                    if quest_obj.author_id != auth.get_user(request).id and not auth.get_user(request).id in list_of_players:
                        if quest_obj.paid:
                            # есть плата за цчастие
                            args['auth_user'] = auth.get_user(request)
                            args['quest'] = quest_obj
                            args['now'] = Now
                            try:
                                pay_number = str(Part_Order.objects.get(quest_id=quest_id,
                                                                        user_id=auth.get_user(request).id).uuid)[1::]
                            except Exception as err:
                                pay_number = ''.join([random.choice(list('0123456789ADFCB')) for x in range(12)])
                            args['pay_number'] = pay_number
                            return render(request, 'qworld/requests/part_pay_form.html', args)
                        else:
                            # нет платы за участие
                            quest_obj.participants += 1
                            quest_obj.save()
                            user = ExtUser.objects.get(id=auth.get_user(request).id)
                            user.level_points += 220
                            if user.level_points >= 1000:
                                user.level_points -= 1000
                                user.level += 1
                            user.save()
                            player = Player(player_id=auth.get_user(request).id, completed_percent=0, for_quest=quest_obj)
                            player.save()
                            participated_quest = Participated_quest(quest_id=quest_id, for_user=auth.get_user(request))
                            participated_quest.save()
                            args['quest'] = quest_obj
                            args['auth_user'] = auth.get_user(request)
                            attr = {}
                            attr['auth_user'] = auth.get_user(request)
                            attr['quest'] = quest_obj 
                            to = auth.get_user(request).email
                            subject, from_email = 'Уведомление об участии в квесте', EMAIL_HOST_USER
                            html_content = get_template('email/participate.html').render(Context(attr))
                            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            return render(request, 'qworld/quest_wait_of_begin.html', args)
                    else:
                        # вы уже участвовуете
                        return redirect('quest', quest_id)
                else:
                    # не пытайтесь поставить свои правила
                    return redirect('found')
            else:
                args['password_err'] = True
                args['quest'] = quest_obj
                args['auth_user'] = auth.get_user(request)
                return render(request, 'qworld/quest_participate.html', args)
    else:
        return redirect('/')


@csrf_exempt
def support(request):
    if request.user.is_authenticated():
        args = {}
        args['auth_user'] = auth.get_user(request)
        if request.method == 'POST':
            payload = {'secret': '6LeUTSsUAAAAACuIG4UccPsZ7eiBman2usBEGXv3',
                       'response': str(request.POST['g-recaptcha-response'])}
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
            is_user = r.text.replace("{", "").replace("}", "").split(",")[0].split(":")[1]
            if is_user.replace(" ","") == 'true':
                form = SupportMessageForm(request.POST)
                try:
                    title = request.POST['title']
                except Exception as err:
                    title = None
                if title is None:
                    args['title_err'] = True
                    args['SupportMessageForm'] = form
                    return render_to_response('support/support.html', args)
                else:
                    to = ''
                    if title == '1':
                        to = 'qWorldSupportIm@yandex.ru'  # Предложения
                    elif title == '2':
                        to = 'qWorldSupportHl@yandex.ru'  # Помощь
                    elif title == '3':
                        to = 'qWorldSupportWr@yandex.ru'  # Жалоба
                    if to != '' and request.POST['topic'] != '' and not request.POST['topic'].isspace() and request.POST['text'] != '' and not request.POST['text'].isspace():
                        form.email = auth.get_user(request).email
                        args['text'] = request.POST['text']
                        subject, from_email = request.POST['topic'], EMAIL_HOST_USER
                        html_content = get_template('email/support.html').render(Context(args))
                        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        attr = {}
                        attr['auth_user'] = auth.get_user(request)
                        to = auth.get_user(request).email
                        subject, from_email = 'Обращение в службу поддержки', EMAIL_HOST_USER
                        html_content = get_template('email/support_for_user.html').render(Context(attr))
                        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return render_to_response('support/agree_message.html', args)
                    else:
                        return redirect('support')
            else:
                return redirect('support')
        else:
            args['SupportMessageForm'] = SupportMessageForm()
            return render_to_response('support/support.html', args)
    else:
        return redirect('/')


@csrf_exempt
def group_log_in(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            args = {}
            quest_id = int(request.POST['quest_id'])
            group_name = request.POST['group_name']
            admin_log = request.POST['group_admin_log']
            admin_pass = request.POST['group_admin_pass']
            args['correct'] = False
            obj_quest = Quest.objects.get(id=quest_id)
            if obj_quest.author_id != auth.get_user(request).id:
                try:
                    group = Quest_Group.objects.get(name__contains=group_name, for_quest=obj_quest)
                    players = []
                    for player in Group_Player.objects.all().filter(for_group=group):
                        players.append(player.player_id)
                    in_group = False
                    if auth.get_user(request).id in players:
                        in_group = True
                    if group.admin_login == admin_log and group.admin_password == admin_pass and in_group:
                        cords = []
                        waypoints = Waypoint.objects.all().filter(for_quest=obj_quest, for_gid=group.id)
                        for waypoint in waypoints:
                            waypoint.code = ''
                            cords.append([float(waypoint.address_d), float(waypoint.address_s)])
                        args['waypoints'] = waypoints
                        args['quest'] = obj_quest
                        args['cords'] = cords
                        args['group_completed'] = group.completed
                        args['result'] = group.completed_percent
                        args['gr_id'] = group.id
                        return render_to_response('qworld/requests/group_log_in.html', args)
                    else:
                        return JsonResponse(args)
                except Exception as err:
                    return JsonResponse(args)
            else:
                redirect('quest', quest_id)
        else:
            return redirect('found')
    else:
        return redirect('/')


def upgradeachievement(user, result):
    achievements = Achievement_user.objects.all().filter(for_user=user)
    set1 = (1, 2, 3)
    for achievement in achievements:
        if achievement.achiev_id in set1:
            max_score = Achievement.objects.get(id=achievement.achiev_id).max_score
            if achievement.min_score < max_score:
                achievement.min_score += 1
                achievement.save()
        if achievement.achiev_id == 4:
            max_score = Achievement.objects.get(id=achievement.achiev_id).max_score
            if achievement.min_score < max_score and result == 100:
                achievement.min_score += 1
                achievement.save()


@csrf_exempt
def group_end(request, quest_id=0, group_id=0):
    if request.user.is_authenticated():
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        obj_quest = get_object_or_404(Quest, id=quest_id)
        if obj_quest.begin_date_time <= Now <= obj_quest.end_date_time:
            if request.method == 'POST':
                if obj_quest.author_id == auth.get_user(request).id:
                    # вы не можете изменять квест во время того как он идёт
                    args['quest'] = obj_quest
                    return render(request, 'qworld/quest_cant_change.html', args)
                else:
                    group = Quest_Group.objects.get(id=group_id)
                    list_of_players = []
                    result = 0.0
                    try:
                        players = Group_Player.objects.all().filter(for_group=group)
                        for player in players:
                            list_of_players.append(player.player_id)
                    except Exception as err:
                        list_of_players = []
                    if auth.get_user(request).id in list_of_players:
                        if int(request.POST.get('like')) == 1:
                            obj_quest.likes += 1
                            obj_quest.save()
                        elif int(request.POST.get('like')) == 2:
                            obj_quest.dislikes += 1
                            obj_quest.save()
                        else:
                            pass
                        right_codes = []
                        for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest, for_gid=group.id):
                            right_codes.append(waypoint.code)
                        codes = request.POST.getlist('code')
                        per = 100 / len(codes)
                        part_per = 0.0
                        for code in codes:
                            for right_code in right_codes:
                                str = right_code.replace(' ', '').lower()
                                str2 = code.replace(' ', '').lower()
                                if str.find(str2) != -1:
                                    part_per = + len(str2)/len(str)
                            result += part_per * per
                        gr = Quest_Group.objects.get(id=group_id)
                        gr.completed = True
                        gr.completed_percent = int(result)
                        gr.save()
                        gr_players = Group_Player.objects.all().filter(for_group=gr)
                        for gr_layer in gr_players:
                            user = ExtUser.objects.get(id=gr_layer.player_id)
                            user.level_points += int(350 * result)
                            if user.level_points >= 1000:
                                user.level_points -= 1000
                                user.level += 1
                            user.save()
                            upgradeachievement(user, int(result))
                        args['auth_user'] = auth.get_user(request)
                        args['quest'] = obj_quest
                        args['result'] = int(result)
                        return render_to_response('qworld/requests/end_group.html', args)
                    else:
                        return redirect('quest', quest_id)
            else:
                return redirect('quest', quest_id)
        else:
            return redirect('quest', quest_id)
    else:
        return redirect('/')


@csrf_exempt
def end(request, quest_id=0):
    if request.user.is_authenticated():
        args = {}
        Now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        obj_quest = get_object_or_404(Quest, id=quest_id)
        if obj_quest.begin_date_time <= Now <= obj_quest.end_date_time:
            if request.method == 'POST':
                if obj_quest.author_id == auth.get_user(request).id:
                    # вы не можете изменять квест во время того как он идёт
                    args['quest'] = obj_quest
                    return render(request, 'qworld/quest_cant_change.html', args)
                else:
                    list_of_players = []
                    result = 0.0
                    try:
                        players = Player.objects.all().filter(for_quest=obj_quest)
                        for player in players:
                            list_of_players.append(player.player_id)
                    except Exception as err:
                        list_of_players = []
                    if auth.get_user(request).id in list_of_players:
                        if int(request.POST.get('like')) == 1:
                            obj_quest.likes += 1
                            obj_quest.save()
                        elif int(request.POST.get('like')) == 2:
                            obj_quest.dislikes += 1
                            obj_quest.save()
                        else:
                            pass
                        right_codes = []
                        for waypoint in Waypoint.objects.all().filter(for_quest=obj_quest):
                            right_codes.append(waypoint.code)
                        codes = request.POST.getlist('code')
                        per = 100 / len(codes)
                        part_per = 0.0
                        for code in codes:
                            for right_code in right_codes:
                                str = right_code.replace(' ', '').lower()
                                str2 = code.replace(' ', '').lower()
                                if str.find(str2) != -1:
                                    part_per = + len(str2)/len(str)
                            result += part_per * per
                        pl = Player.objects.get(for_quest=obj_quest, player_id=auth.get_user(request).id)
                        pl.completed = True
                        pl.completed_percent = int(result)
                        pl.save()
                        user = ExtUser.objects.get(id=auth.get_user(request).id)
                        user.level_points += int(450 * result)
                        if user.level_points >= 1000:
                            user.level_points -= 1000
                            user.level += 1
                        user.save()
                        upgradeachievement(user, int(result))
                        args['completed'] = True
                        args['auth_user'] = auth.get_user(request)
                        args['quest'] = obj_quest
                        args['result'] = int(result)
                        return render(request, 'qworld/quest_is_going.html', args)
                    else:
                        return redirect('quest', quest_id)
            else:
                return redirect('quest', quest_id)
        else:
            return redirect('quest', quest_id)
    else:
        return redirect('/')


@csrf_exempt
def get_html_checkbox_photo(request, quest_id):
    quest_obj = Quest.objects.get(id=quest_id)
    photos = []
    k = 0
    for photo in Photo.objects.all().filter(for_quest=quest_obj):
        k += 1
        photo.key = k
        photos.append(photo)
    args = {}
    args['photos'] = photos
    return render_to_response('qworld/requests/quest_photos.html', args)


@csrf_exempt
def get_html_normal_photo(request, quest_id):
    quest_obj = Quest.objects.get(id=quest_id)
    photos = []
    for photo in Photo.objects.all().filter(for_quest=quest_obj):
        photos.append(photo)
    args = {}
    args['photos'] = photos
    return render_to_response('qworld/requests/quest_photos_normal.html', args)


@csrf_exempt
def save_quest_photos(request, quest_id):
    args = {}
    quest_obj = Quest.objects.get(id=quest_id)
    if quest_obj.author_id == auth.get_user(request).id:
        try:
            len_photo = int(request.POST['len'])
            delete_photos = set()
            for i in range(1, len_photo + 1):
                st = request.POST.get(str(i))
                data = st.split(',')
                if data[1] == 'true':
                    delete_photos.add(int(data[0]))
            for photo in Photo.objects.all().filter(for_quest=quest_obj):
                if photo.id in delete_photos:
                    os.remove(MEDIA_ROOT + '/' + photo.photo.name)
                    photo.delete()
            for file in request.FILES.getlist('quest_photos'):
                try:
                    f = Photo(photo=file, for_quest=quest_obj)
                    f.save()
                except Exception as err:
                    pass
            photos = []
            for photo in Photo.objects.all().filter(for_quest=quest_obj):
                photos.append(photo)
            args['photos'] = photos
            return render_to_response('qworld/requests/new_photos.html', args)
        except Exception as err:
            return HttpResponse(err)
