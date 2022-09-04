from django import forms
from .models import User, SchedulingSystem
from django.contrib.auth import authenticate
from django.forms import ModelForm, DateInput, RadioSelect, TextInput, Select
from datetime import date


class DayInput(forms.DateInput):
    input_type = 'date'


class RegisterForm(forms.Form):
    username = forms.CharField(label='Придумайте username', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Имя', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', max_length=60, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    grade = forms.ChoiceField(choices=[('9', '9-6'), ('9', '9-7'), ('10', '10-6'), ('10', '10-7')], widget=forms.Select(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Придумайте пароль', max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Введите пароль еще раз', max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    rule_check = forms.BooleanField(label='Я согласен с правилами сайта', required=True, widget=forms.CheckboxInput(attrs={}))

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")


class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Введите свой username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not authenticate(username=username, password=password):
            raise forms.ValidationError('Invalid login')


class SchSysForm1(forms.ModelForm):
    def __init__(self, choices, *args, **kwargs):
        super(SchSysForm1, self).__init__(*args, **kwargs)
        self.fields['task'] = forms.ChoiceField(choices=choices)
        self.fields['task'].widget.attrs['class'] = 'form-control w-50 mx-auto'

    class Meta:
        model = SchedulingSystem
        fields = ('task',)
        # widgets = {'task': DateInput(attrs={'class': 'form-control w-50 mx-auto'})}


class SchSysForm2(forms.ModelForm):
    class Meta:
        model = SchedulingSystem
        fields = ('day',)
        widgets = {'day': DateInput(attrs={'class': 'datepicker form-control w-50 mx-auto'})}


class SchSysForm3(forms.ModelForm):
    def __init__(self, choices, *args, **kwargs):
        super(SchSysForm3, self).__init__(*args, **kwargs)
        self.fields['time'] = forms.ChoiceField(choices=choices, initial='1')
        self.fields['time'].widget.attrs['class'] = 'form-control w-50 mx-auto'

    class Meta:
        model = SchedulingSystem
        fields = ('time', 'additional_info')
        widgets = {'additional_info': TextInput(attrs={'class': 'textarea form-control input-lg w-75 mh-200 mx-auto'})}
