from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from user_profile.models import  ExtUser, User_photo


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Подтверждение',
        widget=forms.PasswordInput
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароль и подтверждение не совпадают')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('email',)


class UserChangeForm(forms.ModelForm):

    '''
    Форма для обновления данных пользователей. Нужна только для того, чтобы не
    видеть постоянных ошибок "Не заполнено поле password" при обновлении данных
    пользователя.
    '''
    password = ReadOnlyPasswordHashField(
        widget=forms.PasswordInput,
        required=False
    )

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        password = self.cleaned_data["password"]
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ['email', ]


class LoginForm(forms.Form):

    """Форма для входа в систему
    """
    username = forms.CharField()
    password = forms.CharField()


class UserChangeProfileData(forms.Form, forms.ModelForm):
    avatar = forms.FileField(widget=forms.FileInput(), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = ReadOnlyPasswordHashField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = ExtUser
        fields = ('email', 'username', 'avatar', 'firstname', 'lastname', 'about_user',
                  'middlename', 'date_of_birth', 'phone', 'sb_can_rt_com', 'sb_can_wt_quests')

    def save(self, commit=True):
        change = super(UserChangeProfileData, self).save(commit=False)
        password = self.cleaned_data["password"]
        if password and password != '' and not password.isspace():
            change.set_password(password)
        if commit:
            change.save()
        return change

