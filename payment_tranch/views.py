import random
import hashlib
from django.contrib import auth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from q.settings import EMAIL_HOST_USER
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from payment_tranch.models import Promocode, Order, Part_Order
from qworld.models import Quest, Player, Quest_Group, Group_Player
from user_profile.models import Waiting_quest, Created_quest, ExtUser, Participated_quest
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
Now = timezone.now()
# Create your views here.


def payment(request, quest_id):
    args = {}
    if request.user.is_authenticated():
        args['auth_user'] = auth.get_user(request)
        quest = get_object_or_404(Quest, id=quest_id)
        args['quest'] = quest
        if quest.mon_paid is False:
            args['now'] = Now
            try:
                pay_number = str(Order.objects.get(quest_id=quest_id).uuid)[1::]
            except Exception as err:
                pay_number = ''.join([random.choice(list('0123456789ADFCB')) for x in range(12)])
            args['pay_number'] = pay_number
            return render_to_response('qworld/payment.html', args)
        else:
            return render_to_response('qworld/payment_is_ok.html', args)
    else:
        return redirect('/')


@csrf_exempt
def checkcode(request):
    if request.method == 'POST':
        code = request.POST['code']
        args = {}
        codes = set()
        args['isvalid'] = False
        args['discount'] = 0
        for c in Promocode.objects.all():
            codes.add(c.code)
        if code in codes:
            args['isvalid'] = True
            args['discount'] = Promocode.objects.get(code=code).discount
        return JsonResponse(args)


def mail(user_id, payment_num, subject, quest_id):
    attr = {}
    attr['auth_user'] = ExtUser.objects.get(id=user_id)
    attr['payment_num'] = payment_num
    attr['quest'] = Quest.objects.get(id=quest_id)
    if Quest.objects.get(id=quest_id).have_group:
        attr['groups'] = Quest_Group.objects.all().filter(for_quest=Quest.objects.get(id=quest_id))
    to = ExtUser.objects.get(id=user_id).email
    subject, from_email = subject, EMAIL_HOST_USER
    html_content = get_template('email/success_pay.html').render(Context(attr))
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return 0


def mail_part(user_id, payment_num, subject, quest_id):
    attr = {}
    attr['auth_user'] = ExtUser.objects.get(id=user_id)
    attr['payment_num'] = payment_num
    attr['quest'] = Quest.objects.get(id=quest_id)
    to = ExtUser.objects.get(id=user_id).email
    subject, from_email = subject, EMAIL_HOST_USER
    html_content = get_template('email/success_part_pay.html').render(Context(attr))
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return 0


@csrf_exempt
def y_success(request):
    if request.method == 'POST':
        hash = hashlib.sha1(str(request.POST['notification_type'] + '&' + request.POST['operation_id'] +  \
            '&' + request.POST['amount'] + '&' + request.POST['currency'] + \
            '&' + request.POST['datetime'] + '&' + request.POST['sender'] + '&' + request.POST['codepro'] + \
            '&' + '...' + '&' + request.POST['label']).encode('utf-8')).hexdigest()
        lab_list = request.POST['label'].split('|')
        action = int(lab_list[0])
        if action == 1:
            pnum = lab_list[1]
            quest_id = int(lab_list[2])
            user_id = int(lab_list[3])
            if str(request.POST['notification_type']) == 'p2p-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['codepro']) == 'false' and str(request.POST['unaccepted']) == 'false':
                    Waiting_quest.objects.get(quest_id=quest_id).delete()
                    cr = Created_quest(for_user=ExtUser.objects.get(id=user_id), quest_id=quest_id)
                    cr.save()
                    order = Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]), uuid=pnum, quest_id=quest_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.mon_paid = True
                    mail(user_id,pnum,'Оповещение об успешной оплате', quest_id)
                    quest.save()
                    return HttpResponse(200)
            elif str(request.POST['notification_type']) == 'card-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['unaccepted']) == 'false':
                    Waiting_quest.objects.get(quest_id=quest_id).delete()
                    cr = Created_quest(for_user=ExtUser.objects.get(id=user_id), quest_id=quest_id)
                    cr.save()
                    order = Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]), uuid=pnum, quest_id=quest_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.mon_paid = True
                    mail(user_id,pnum,'Оповещение об успешной оплате', quest_id)
                    quest.save()
                    return HttpResponse(200)
            return None
        elif action == 2:
            pnum = lab_list[1]
            quest_id = int(lab_list[2])
            user_id = int(lab_list[3])
            if str(request.POST['notification_type']) == 'p2p-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['codepro']) == 'false' and str(
                        request.POST['unaccepted']) == 'false':
                    order = Part_Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]),
                                  uuid=pnum, quest_id=quest_id, user_id=user_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.participants += 1
                    quest.save()
                    author = ExtUser.objects.get(id=quest.author_id)
                    author.money += int(str(request.POST['withdraw_amount']).split('.')[0])
                    author.save()
                    user = ExtUser.objects.get(id=user_id)
                    user.level_points += 220
                    if user.level_points >= 1000:
                        user.level_points -= 1000
                        user.level += 1
                    user.save()
                    player = Player(player_id=user_id, completed_percent=0, for_quest=quest)
                    player.save()
                    participated_quest = Participated_quest(quest_id=quest_id, for_user=ExtUser.objects.get(id=user_id))
                    participated_quest.save()
                    mail_part(user_id, pnum,'Оповещение об успешной оплате участия', quest_id)
                    return HttpResponse(200)
            elif str(request.POST['notification_type']) == 'card-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['unaccepted']) == 'false':
                    order = Part_Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]),
                                       uuid=pnum, quest_id=quest_id, user_id=user_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.participants += 1
                    quest.save()
                    author = ExtUser.objects.get(id=quest.author_id)
                    author.money += int(str(request.POST['withdraw_amount']).split('.')[0])
                    author.save()
                    user = ExtUser.objects.get(id=user_id)
                    user.level_points += 220
                    if user.level_points >= 1000:
                        user.level_points -= 1000
                        user.level += 1
                    user.save()
                    player = Player(player_id=user_id, completed_percent=0, for_quest=quest)
                    player.save()
                    participated_quest = Participated_quest(quest_id=quest_id, for_user=ExtUser.objects.get(id=user_id))
                    participated_quest.save()
                    mail_part(user_id, pnum,'Оповещение об успешной оплате участия', quest_id)
                    return HttpResponse(200)
            return None
        elif action == 3:
            pnum = lab_list[1]
            quest_id = int(lab_list[2])
            user_id = int(lab_list[3])
            if str(request.POST['notification_type']) == 'p2p-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['codepro']) == 'false' and str(
                        request.POST['unaccepted']) == 'false':
                    order = Part_Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]),
                                  uuid=pnum, quest_id=quest_id, user_id=user_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.participants += 1
                    quest.save()
                    author = ExtUser.objects.get(id=quest.author_id)
                    author.money += int(str(request.POST['withdraw_amount']).split('.')[0])
                    author.save()
                    group_id = int(lab_list[4])
                    group_obj = Quest_Group.objects.get(for_quest=quest, id=group_id)
                    group_player = Group_Player(for_group=group_obj, player_id=user_id)
                    group_player.save()
                    player = Player(player_id=user_id, completed_percent=0, for_quest=quest)
                    player.save()
                    user = ExtUser.objects.get(id=user_id)
                    user.level_points += 140
                    if user.level_points >= 1000:
                        user.level_points -= 1000
                        user.level += 1
                    user.save()
                    participated_quest = Participated_quest(quest_id=quest_id, for_user=ExtUser.objects.get(id=user_id))
                    participated_quest.save()
                    mail_part(user_id, pnum,'Оповещение об успешной оплате участия', quest_id)
                    return HttpResponse(200)
            elif str(request.POST['notification_type']) == 'card-incoming':
                if str(request.POST['sha1_hash']) == str(hash) and str(request.POST['unaccepted']) == 'false':
                    order = Part_Order(count=1, amount=int(str(request.POST['withdraw_amount']).split('.')[0]),
                                       uuid=pnum, quest_id=quest_id, user_id=user_id)
                    order.save()
                    quest = Quest.objects.get(id=quest_id)
                    quest.participants += 1
                    quest.save()
                    author = ExtUser.objects.get(id=quest.author_id)
                    author.money += int(str(request.POST['withdraw_amount']).split('.')[0])
                    author.save()
                    group_id = int(lab_list[4])
                    group_obj = Quest_Group.objects.get(for_quest=quest, id=group_id)
                    group_player = Group_Player(for_group=group_obj, player_id=user_id)
                    group_player.save()
                    player = Player(player_id=user_id, completed_percent=0, for_quest=quest)
                    player.save()
                    user = ExtUser.objects.get(id=user_id)
                    user.level_points += 140
                    if user.level_points >= 1000:
                        user.level_points -= 1000
                        user.level += 1
                    user.save()
                    participated_quest = Participated_quest(quest_id=quest_id, for_user=ExtUser.objects.get(id=user_id))
                    participated_quest.save()
                    mail_part(user_id, pnum,'Оповещение об успешной оплате участия', quest_id)
                    return HttpResponse(200)
            return None
        return None


@csrf_exempt
def pay(request, quest_id):
    if request.method == 'POST':
        amount = 600
        pnum = request.POST.get('pay_number')
        try:
            code = request.POST.get('code')
            codes = set()
            for c in Promocode.objects.all():
                codes.add(c.code)
            if code in codes:
                c = Promocode.objects.all().filter(code=code)
                amount = amount * (100 - int(c[0].discount)) / 100
        except Exception as err:
            code = ''
        args = {}
        if int(amount) == 0:
            args['auth_user'] = auth.get_user(request)
            Waiting_quest.objects.get(quest_id=quest_id).delete()
            cr = Created_quest(for_user=auth.get_user(request), quest_id=quest_id)
            cr.save()
            order = Order(count=1, amount=amount, uuid=pnum, quest_id=quest_id)
            order.save()
            quest = Quest.objects.get(id=quest_id)
            quest.mon_paid = True
            quest.save()
            args['quest'] = quest
            return render_to_response('qworld/requests/success.html', args)
        if int(amount) > 0:
            args['yandex_money_account'] = "..."
            args['quest'] = Quest.objects.get(id=quest_id)
            args['pnum'] = pnum
            args['amount'] = amount
            args['auth_user'] = auth.get_user(request)
            return render_to_response('qworld/requests/pay_form.html', args)



@csrf_exempt
def part_pay(request, quest_id, group_id=0):
    if request.method == 'POST':
        quest = Quest.objects.get(id=quest_id)
        if quest.mon_paid:
            pnum = request.POST.get('pay_number')
            args = {}
            args['yandex_money_account'] = "..."
            args['quest'] = quest
            args['pnum'] = pnum
            args['amount'] = quest.cost
            args['auth_user'] = auth.get_user(request)
            if quest.have_group:
                args['group_id'] = group_id
            return render_to_response('qworld/requests/part_pay_form_modal.html', args)