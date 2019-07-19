from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import UserChangeForm
from .forms import UserCreationForm
from .models import ExtUser, Participated_quest, Created_quest, User_photo,\
    Achievement, Achievement_user, Waiting_quest


class Part_Quest_Line(admin.StackedInline):
    model = Participated_quest
    extra = 1


class Created_Quest_Line(admin.StackedInline):
    model = Created_quest
    extra = 1


class Waiting_Quest_Line(admin.StackedInline):
    model = Waiting_quest
    extra = 1


class User_Photos_Line(admin.StackedInline):
    model = User_photo
    extra = 1


class User_Achievement_Line(admin.StackedInline):
    model = Achievement_user
    extra = 1


class UserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = [
        'id',
        'username',
        'email',
        'firstname',
        'lastname',
        'middlename',
        'date_of_birth',
        'is_superuser',
    ]

    list_filter = ('is_admin',)

    fieldsets = (
                (None, {'fields': ('email', 'username','password')}),
                ('Personal info', {
                 'fields': (
                     'avatar',
                     'date_of_birth',
                     'level',
                     'level_points',
                     'firstname',
                     'lastname',
                     'middlename',
                     'money',
                     'phone',
                     'about_user',
                 )}),
                ('Privacy', {'fields': ('sb_can_rt_com', 'sb_can_wt_quests',)}),
                ('Permissions', {'fields': ('is_admin', 'is_superuser')}),
                ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
		'username',
                'email',
                'password1',
                'password2',
		'is_admin',
		'is_superuser',
            )}
         ),
    )

    search_fields = ('email',)
    ordering = ('email',)
    inlines = [ Part_Quest_Line, Created_Quest_Line,
               User_Photos_Line, User_Achievement_Line, Waiting_Quest_Line]
    filter_horizontal = ()

# Регистрация нашей модели
admin.site.register(ExtUser, UserAdmin)
admin.site.register(Achievement)
#admin.site.unregister(Group)
admin.site.register(Created_quest)
