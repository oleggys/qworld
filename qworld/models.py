from django.db import models
# Create your models here.


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Категории'
    name = models.CharField(max_length=40, verbose_name='Категория')

    def __str__(self):
        return self.name


class Quest(models.Model):
    class Meta():
        verbose_name_plural = 'Квест'

    avatar = models.ImageField(upload_to='quest_avatar', blank=True)
    name = models.CharField(max_length=150, verbose_name='Название')
    have_password = models.BooleanField(verbose_name='С паролем', default=False)
    password = models.CharField(max_length=20, verbose_name='Пароль', blank=True)
    author_id = models.IntegerField(verbose_name='id Автора', default=0, blank=True)
    have_group = models.BooleanField(default=False, verbose_name='С группами')
    target = models.TextField(verbose_name='Цель')
    description = models.TextField(verbose_name='Описание')
    town = models.CharField(max_length=100, verbose_name='Город', blank=True)
    begin_date_time = models.DateTimeField(verbose_name='Начало')
    end_date_time = models.DateTimeField(verbose_name='Конец')
    meeting_point = models.CharField(max_length=200, verbose_name='Место встречи')
    meeting_date_time = models.DateTimeField(verbose_name='Время встречи')
    category = models.ManyToManyField(Category, verbose_name='Категории', blank=True)
    likes = models.IntegerField(default=0, verbose_name='Лайки')
    dislikes = models.IntegerField(default=0, verbose_name='Диздайки')
    participants = models.IntegerField(default=0, verbose_name='Участники')
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    paid = models.BooleanField(default=False, verbose_name='Есть плата за участие')
    cost = models.IntegerField(default=0, verbose_name='Цена участия', blank=True, null=True)
    mon_paid = models.BooleanField(default=False, verbose_name='Оплачен')

    def __str__(self):
        return self.name

    def shot_target(self):
        if len(self.target) > 150:
            return self.target[:150]
        else:
            return self.target


def quest_photo_directory_avatar_path(instance, filename):
    return 'quest_photo/{0}/{1}'.format(instance.for_quest.id, filename)


class Photo(models.Model):
    class Meta:
        verbose_name_plural = 'Фотографии'
    photo = models.ImageField(verbose_name='Фотография', upload_to=quest_photo_directory_avatar_path)
    for_quest = models.ForeignKey(Quest)



class Quest_Group(models.Model):
    name = models.CharField(max_length=70, verbose_name='Название')
    admin_login = models.CharField(max_length=50, verbose_name='Login админа')
    admin_password = models.CharField(max_length=50, verbose_name='Пароль админа')
    completed = models.BooleanField(default=False)
    completed_percent = models.IntegerField(default=0)
    for_quest = models.ForeignKey(Quest)

    def __str__(self):
        return self.name

class Waypoint(models.Model):
    address_s = models.CharField(max_length=9, verbose_name='Широта')
    address_d = models.CharField(max_length=9, verbose_name='Долгота')
    for_gid = models.IntegerField(verbose_name='Для группы', default=0)
    tip = models.TextField(verbose_name='Подсказка')
    code = models.CharField(max_length=100, verbose_name='Код')
    for_quest = models.ForeignKey(Quest)
    def __str__(self):
        return self.tip

class Player(models.Model):
    player_id = models.IntegerField()
    completed = models.BooleanField(default=False)
    completed_percent = models.IntegerField()
    for_quest = models.ForeignKey(Quest)


class Group_Player(models.Model):
    player_id = models.IntegerField()
    for_group = models.ForeignKey(Quest_Group)


class Questions(models.Model):
    class Meta:
        verbose_name_plural = 'Вопросы'

    question = models.CharField(max_length=200, verbose_name='Вопрос')
    text = models.TextField('Ответ')

    def __str__(self):
        return self.question
