import datetime

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Email непременно должен быть указан')
        if len(username) < 6:
            raise ValueError('Длина логина должна быть больше 5')

        user = self.model(
            email=UserManager.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


def user_directory_avatar_path(instance, filename):
    return 'users/avatar/{0}/{1}'.format(instance.username, 'avatar.png')


class ExtUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('username', max_length=20, unique=True, db_index=True)
    email = models.EmailField('Электронная почта', max_length=30, unique=True, db_index=True)
    level = models.IntegerField('Уровень', default=0, blank=True)
    level_points = models.IntegerField('Очки для уровня', default=0, blank=True)
    avatar = models.ImageField('Аватар', blank=True, upload_to=user_directory_avatar_path,
                               default='default_user_avatar.png')
    firstname = models.CharField('Имя', max_length=40, null=True, blank=True)
    lastname = models.CharField('Фамилия', max_length=40, null=True, blank=True)
    middlename = models.CharField('Отчество', max_length=40, null=True, blank=True)
    money = models.IntegerField('Баланс', default=0)
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
    register_date = models.DateField('Дата регистрации', auto_now_add=True)
    phone = models.CharField('Телефон', max_length=15, null=True, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    is_admin = models.BooleanField('Суперпользователь', default=False)
    about_user = models.TextField('О пользователе', blank=True)
    sb_can_rt_com = models.BooleanField(default=True, blank=True,
                                        verbose_name='Кто-нибудь может оставлять коментарии')
    sb_can_wt_quests = models.BooleanField(default=True, blank=True,
                                           verbose_name='Кто-нибудь может смотреть участие и создание квестов')

    # Этот метод обязательно должен быть определён
    def get_full_name(self):
        return self.username

    # Требуется для админки
    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



class Participated_quest(models.Model):
    class Meta():
        verbose_name_plural = 'Квесты с участием человека'
    quest_id = models.IntegerField()
    for_user = models.ForeignKey(ExtUser)


class Created_quest(models.Model):
    class Meta():
        verbose_name_plural = 'Созданные квесты'
    quest_id = models.IntegerField()
    for_user = models.ForeignKey(ExtUser)


class Waiting_quest(models.Model):
    class Meta():
        verbose_name_plural = 'Неоплаченные квесты'
    quest_id = models.IntegerField()
    for_user = models.ForeignKey(ExtUser)


def user_directory_path(instance, filename):
    return 'users/photos/{0}/{1}'.format(instance.for_user.username, filename)


class User_photo(models.Model):
    class Meta:
        verbose_name_plural = 'Фотографии'

    for_user = models.ForeignKey(ExtUser)
    photo = models.ImageField('Фотография', upload_to=user_directory_path)


class Achievement(models.Model):
    class Meta:
        verbose_name_plural = 'Достижения'

    avatar = models.ImageField('Картинка', upload_to='achievements')
    name = models.CharField('Название ачивки', max_length=100)
    description = models.TextField('Описание')
    max_score = models.IntegerField('Максимальное количество очков', blank=True)

    def __str__(self):
        return self.name


class Achievement_user(models.Model):
    class Meta:
        verbose_name_plural = 'Достяжения пользователя'

    achiev_id = models.IntegerField('id достяжения')
    min_score = models.IntegerField('Сколько сейчас очков', default=0)
    for_user = models.ForeignKey(ExtUser)
