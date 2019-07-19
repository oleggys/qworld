import random
import requests
from django.contrib import auth
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, render
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from loginsys.forms import RegistrationForm
from q.settings import EMAIL_HOST_USER
from user_profile.models import ExtUser, Achievement, Achievement_user
from django.template.loader import get_template
from django.template import Context
import hashlib


@csrf_exempt
def login(request):
    args = {}
    args.update(csrf(request))
    if request.user.is_authenticated():
        return redirect('/')
    else:
        if request.POST:
            username = request.POST.get('username1', '')
            password = request.POST.get('password1', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('profile', auth.get_user(request).username)
            else:
                args['login_error'] = "Неверный логин или пароль"
                return render_to_response('loginsys/login.html', args)
        else:
            return render_to_response('loginsys/login.html', args)


def logout(request):
    auth.logout(request)
    return redirect('index')


@csrf_exempt
def reminde(request):
    args = {}
    if request.user.is_authenticated():
        return redirect('quest/found')
    else:
        if request.POST:
            payload = {'secret': '6LeUTSsUAAAAACuIG4UccPsZ7eiBman2usBEGXv3', 'response': str(request.POST.get('recaptcha'))}
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
            is_user = r.text.replace("{", "").replace("}", "").split(",")[0].split(":")[1]
            if is_user.replace(" ","") == 'true':
                email = request.POST.get('email', '')
                try:
                    user = ExtUser.objects.get(email=email)    
                    try:
                        attr = {}
                        attr['auth_user'] = user
                        code = ''.join([random.choice(list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXZabcdefghijklmnopqrst')) for x in range(10)]) + str(user.id)
                        attr['code'] = code
                        cr_code = hashlib.md5(code.encode('utf-8')).hexdigest()
                        cr_code = hashlib.md5(cr_code.encode('utf-8')).hexdigest()
                        args['crypt_code'] = hashlib.sha1(cr_code.encode('utf-8')).hexdigest()
                        to = user.email
                        subject, from_email = 'Восстановление пароля', EMAIL_HOST_USER
                        html_content = get_template('email/reminde.html').render(Context(attr))
                        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        return HttpResponse(get_template('loginsys/new_password.html').render(Context(args)))
                    except Exception as err:
                        return HttpResponse(0)
                except Exception:
                    return HttpResponse(0)
        else:
            return render(request, 'loginsys/reminde_pass.html', args)


@csrf_exempt
def reminde_confirmation(request):
    if request.POST:
        code = request.POST.get('code')
        uid = code[10:]
        code = hashlib.md5(code.encode('utf-8')).hexdigest()
        code = hashlib.md5(code.encode('utf-8')).hexdigest()
        code = str(hashlib.sha1(code.encode('utf-8')).hexdigest())
        cr_code = request.POST.get('cr_code')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        if str(code) == str(cr_code):
            if new_password1 == new_password2:
                user = ExtUser.objects.get(id=uid) 
                user.set_password(new_password2)
                user.save()
                us = auth.authenticate(username=user.username, password=new_password2)
                auth.login(request, us)
                return HttpResponse(2)
            else:
                return HttpResponse(1)
        else:
            return HttpResponse(0)
    else:
        return redirect('/')


def index(request):
    if request.user.is_authenticated():
        return redirect('quest/found')
    else:
        return render(request, 'loginsys/index.html')


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.size
    kilobyte_limit = 20.0
    if filesize > kilobyte_limit * 1024:
        return False
    else:
        return True


@csrf_protect
def registration(request):
    args = {}
    args.update(csrf(request))
    args['form'] = RegistrationForm()
    if request.POST:
        payload = {'secret': '6LeUTSsUAAAAACuIG4UccPsZ7eiBman2usBEGXv3',
                   'response': str(request.POST['g-recaptcha-response'])}
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        is_user = r.text.replace("{", "").replace("}", "").split(",")[0].split(":")[1]
        if is_user.replace(" ","") == 'true':
            newuser_form = RegistrationForm(request.POST, request.FILES)
            try:
                file = request.FILES['avatar']
                havefile = False
            except Exception:
                havefile = True
            if havefile:
                i = True
            else:
                i = validate_image(file)
            if newuser_form.is_valid() and i:
                newuser_form.save(commit=True)
                newuser = auth.authenticate(username=newuser_form.cleaned_data['username'], password=newuser_form.cleaned_data['password2'])
                auth.login(request, newuser)
                try:
                    attr = {}
                    attr['auth_user'] = auth.get_user(request)
                    to = auth.get_user(request).email
                    subject, from_email = 'Регистрация', EMAIL_HOST_USER
                    html_content = get_template('email/registration.html').render(Context(attr))
                    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as err:
                    pass
                for achievement in Achievement.objects.all():
                    ach = Achievement_user(for_user=auth.get_user(request), achiev_id=achievement.id)
                    ach.save()
                return redirect('profile', auth.get_user(request).username)
            else:
                if len(newuser_form.cleaned_data['password1']) < 8:
                    args['password1_error'] = True
                args['form'] = newuser_form
                if not i:
                    args['image_error'] = 'Размер изображения не должне привышать 20Кб'
    return render_to_response('loginsys/registration.html', args)