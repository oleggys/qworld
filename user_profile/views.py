import os
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from loginsys.views import validate_image
from q.settings import MEDIA_ROOT, EMAIL_HOST_USER
from qworld.models import Quest
from payment_tranch.models import Application
from user_profile.forms import UserChangeProfileData
from user_profile.models import ExtUser, Participated_quest, Created_quest, User_photo, Achievement_user, \
    Achievement, Waiting_quest
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
Now = timezone.now()


def profile(request, prof_login=''):
    args = {}
    if request.user.is_authenticated():
        if prof_login == '':
            prof_login = auth.get_user(request).username
        prof_id = get_object_or_404(ExtUser, username=prof_login).id
        part_quest = Participated_quest.objects.filter(for_user=prof_id)
        created_quest = Created_quest.objects.filter(for_user=prof_id)
        if prof_id == auth.get_user(request).id:
            list_of_waiting_quest = {}
            waiting_quest = Waiting_quest.objects.all().filter(for_user=prof_id)
            for q in waiting_quest:
                quest = Quest.objects.get(id=q.quest_id)
                list_of_waiting_quest.update({q.quest_id: quest})
                args['wait_quests'] = list_of_waiting_quest
        list_of_part_quest, list_of_created_quest = {}, {}
        k = 0
        for q in part_quest:
            k += 1
            quest = Quest.objects.get(id=q.quest_id)
            quest.key = k
            list_of_part_quest.update({q.quest_id: quest})
        k = 0
        for q in created_quest:
            k += 1
            quest = Quest.objects.get(id=q.quest_id)
            quest.key = k
            list_of_created_quest.update({q.quest_id: quest})
        args['pr_quests'] = list_of_part_quest
        args['cr_quests'] = list_of_created_quest
        args['auth_user'] = auth.get_user(request)
        args['user'] = get_object_or_404(ExtUser, id=prof_id)
        args['level_points'] = int(args['user'].level_points // 10)
        args['user_photos'] = User_photo.objects.all().filter(for_user=prof_id)
        achievement = Achievement_user.objects.all().filter(for_user=auth.get_user(request))
        achievement_list = {}
        for ach in achievement:
            achive = Achievement.objects.get(id=ach.achiev_id)
            ach.achive_per = int((ach.min_score / achive.max_score) * 100)
            achievement_list.update({achive: ach})
        args['user_achievements'] = achievement_list
        return render(request, 'user_profile/profile.html', args)
    else:
        return redirect('/')


def settings(request):
    args = {}
    if request.user.is_authenticated():
        photos = User_photo.objects.all().filter(for_user=auth.get_user(request).id)
        args['auth_user'] = auth.get_user(request)
        user = ExtUser.objects.get(id=auth.get_user(request).id)
        args['Changeform'] = UserChangeProfileData(request.POST or None, instance=user)
        args['level_points'] = int(auth.get_user(request).level_points // 10)
        args['user_photos'] = photos
        if request.POST:
            args['auth_user'] = auth.get_user(request)
            user = ExtUser.objects.get(id=auth.get_user(request).id)
            change_form = UserChangeProfileData(request.POST, request.FILES, instance=user)
            if change_form.is_valid():
                id_photos = set()
                for photo in photos:
                    id_photos.add(photo.id)
                for photo in photos:
                    ph_id = bool(request.POST.get('photo' + str(photo.id), ''))
                    if ph_id and photo.id in id_photos:
                        photo.delete()
                        os.remove(MEDIA_ROOT + '/' + photo.photo.name)
                if request.FILES.get('photos'):
                    request_photos = request.FILES.getlist('photos')
                    length_photos_obj = len(User_photo.objects.all().filter(for_user=auth.get_user(request)))
                    for photo in request_photos:
                        if length_photos_obj <= 9:
                            length_photos_obj += 1
                            ph = User_photo(photo=photo, for_user=auth.get_user(request))
                            ph.save()
                if request.FILES.get('avatar'):
                    if validate_image(request.FILES['avatar']):
                        try:
                            os.remove(MEDIA_ROOT + '/users/avatar/' + user.username + '/avatar.png')
                        except Exception as err:
                            pass
                    else:
                        args['image_error'] = 'Размер изображения не должне привышать 20Кб'
                        return render(request, 'user_profile/settings.html', args)
                attr = {}
                attr['auth_user'] = auth.get_user(request)
                to = auth.get_user(request).email
                subject, from_email = 'Внесение изменений в профиль', EMAIL_HOST_USER
                html_content = get_template('email/user_settings.html').render(Context(attr))
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                change_form.save()
                if not request.user.is_authenticated():
                    return redirect('/')
                return redirect('profile', auth.get_user(request).username)
            else:
                return render(request, 'user_profile/settings.html', args)
        return render(request, 'user_profile/settings.html', args)
    else:
        return redirect('/')


@csrf_exempt
def get_money(request, prof_login):
    if request.user.is_authenticated():
        if request.POST:
           user = get_object_or_404(ExtUser, username=prof_login)
           if user.id == auth.get_user(request).id:
               if int(request.POST['amount']) <= user.money and user.money != 0:
                   user.money -= int(request.POST['amount'])
                   try:
                       app = Application.objects.get(user_id=user.id, purse=request.POST['purse'])
                       app.amount += int(request.POST['amount'])
                       app.save()
                   except:
                       app = Application(user_id=user.id, amount=int(request.POST['amount']), purse=request.POST['purse'])
                       app.save()
                   user.save()
                   attr = {}
                   attr['money'] = int(request.POST['amount'])
                   attr['purse'] = request.POST['purse']
                   attr['auth_user'] = auth.get_user(request)
                   to = auth.get_user(request).email
                   subject, from_email = 'Отправка заявки на вывод средств', EMAIL_HOST_USER
                   html_content = get_template('email/get_money.html').render(Context(attr))
                   msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                   msg.attach_alternative(html_content, "text/html")
                   msg.send()
                   return HttpResponse(1)  
               else:
                   return HttpResponse(0)  
    else:
        return redirect('/')