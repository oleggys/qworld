from django.contrib import admin
from qworld.models import Quest, Quest_Group, Waypoint, Category, Player, Group_Player, Photo, \
    Questions


class Quest_Group_Line(admin.StackedInline):
    model = Quest_Group
    extra = 1


class Quest_Waypoint_Line(admin.StackedInline):
    model = Waypoint
    extra = 1


class Quest_Player_Line(admin.StackedInline):
    model = Player
    extra = 1


class Quest_Photo_Line(admin.StackedInline):
    model = Photo
    extra = 1


class QuestAdmin(admin.ModelAdmin):
    list_filter = ['begin_date_time']
    list_display = [
        'id',
        'name',
        'author_id',
        'creation_time',
    ]
    inlines = [Quest_Waypoint_Line, Quest_Group_Line, Quest_Player_Line, Quest_Photo_Line]


admin.site.register(Quest, QuestAdmin)
admin.site.register(Category)
admin.site.register(Questions)
admin.site.register(Quest_Group)
admin.site.register(Waypoint)
