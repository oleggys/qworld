from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_profile.models import ExtUser



class RegistrationForm(UserCreationForm, forms.Form):
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'minlength': 5}))
    firstname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    middlename = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ExtUser
        fields = ("avatar", "username", "email", 'firstname', 'lastname', 'middlename', "password1", "password2")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
