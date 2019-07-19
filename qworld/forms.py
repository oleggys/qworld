from django.core.mail import EmailMultiAlternatives
from django.forms import ModelForm, Textarea
from django import forms

from q.settings import EMAIL_HOST_USER
from qworld.models import Quest, Waypoint, Category


def Categ():
    Categories = []
    try:
        for category in Category.objects.all():
            Categories.append((category.id, category))
    except Exception as e:
        pass
    return Categories


class CreateQuestForm(forms.Form, forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    target = forms.CharField(widget=forms.Textarea(attrs={'class': 'md-textarea'}))
    cost = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': '0',
                                                            'value': '0'}),
                              required=False)
    town = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea, required=False)
    meeting_point = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    meeting_date_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'class': 'form-control'}))
    begin_date_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(
        attrs={'class': 'form-control m-2'}))
    end_date_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(
        attrs={'class': 'form-control m-2'}))
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'onchange': 'QuestImageAvatar(this.files[0])'}),
                              required=False)
    category = forms.MultipleChoiceField(required=False,
                                         widget=forms.CheckboxSelectMultiple, choices=Categ())

    class Meta:
        model = Quest
        fields = ('id', 'avatar', 'name', 'have_password', 'password', 'town', 'target', 'description',
                  'begin_date_time', 'end_date_time', 'meeting_point', 'meeting_date_time', 'have_group',
                  'paid', 'cost', 'category', 'author_id')

    def save(self, commit=True):
        quest = super(CreateQuestForm, self).save(commit=False)
        quest.author_id = self.author_id
        categories = self.category
        if commit:
            quest.save()
        for item in list(categories):
            quest.category.add(item)
        if commit:
            quest.save()
        return quest.id


class SupportMessageForm(forms.Form):
    title = forms.IntegerField
    email = forms.CharField()
    topic = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'md-textarea'}), required=True)

