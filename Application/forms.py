from django import forms
from .models import User, SchedulingSystem, DateChanger, TimeInterval
from django.contrib.auth import authenticate
from django.forms import DateInput, TimeInput


class RegisterForm(forms.Form):
    username = forms.CharField(label='Придумайте username', max_length=20, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Имя', max_length=20, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', max_length=20, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', max_length=60, required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    grade = forms.ChoiceField(label='Выберите Ваш класс:', required=True,
                              choices=[('9-5', '9-5'), ('9-6', '9-6'), ('9-7', '9-7'), ('9-9', '9-9'), ('10-6', '10-6'),
                                       ('10-7', '10-7')], widget=forms.Select(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Придумайте пароль', max_length=20, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Введите пароль еще раз', max_length=20, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    rule_check = forms.BooleanField(label='Я согласен с правилами сайта', required=True,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ("email", "username", "password", "grade")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        grade = cleaned_data.get('grade')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if username in User.objects.values_list('username', flat=True):
            self.add_error('username', forms.ValidationError('Никнейм уже занят'))
        if email in User.objects.values_list('email', flat=True):
            self.add_error('email', forms.ValidationError('Email уже привязан'))
        if password1 != password2:
            self.add_error('password2', forms.ValidationError('Пароли различаются'))
        return cleaned_data


class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Введите свой никнейм', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username not in User.objects.values_list('username', flat=True):
            self.add_error('username', forms.ValidationError('Неверный логин'))
        elif not authenticate(username=username, password=password):
            self.add_error('password', forms.ValidationError('Неверный пароль'))


class SchSysForm1(forms.ModelForm):
    def __init__(self, choices, *args, **kwargs):
        super(SchSysForm1, self).__init__(*args, **kwargs)
        self.fields['task'] = forms.ChoiceField(choices=choices)
        self.fields['task'].label = 'Выберите задачу'
        self.fields['task'].widget.attrs['class'] = 'form-control w-75 mx-auto mt-2'
        for k, field in self.fields.items():
            if 'required' in field.error_messages:
                field.error_messages['required'] = 'Пока нет доступных задач для записи'

    class Meta:
        model = SchedulingSystem
        fields = ('task',)


class SchSysForm2(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SchSysForm2, self).__init__(*args, **kwargs)
        self.fields['day'].label = 'Выберите день записи'
        self.fields['day'].widget.attrs['readonly'] = True

    class Meta:
        model = SchedulingSystem
        fields = ('day',)
        widgets = {'day': DateInput(
            attrs={'class': 'datepicker form-control w-50 mx-auto mt-2', 'style': 'background-color: white;'})}

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        if day is None:
            self.add_error('day', forms.ValidationError('Введите дату'))
            return
        if day.weekday() not in [3, 4, 5]:
            self.add_error('day', forms.ValidationError('Некорректная дата'))


class SchSysForm3(forms.ModelForm):
    def __init__(self, choices, *args, **kwargs):
        super(SchSysForm3, self).__init__(*args, **kwargs)
        self.fields['time'] = forms.ChoiceField(choices=choices)
        self.fields['time'].label = 'Выберите время:'
        self.fields['time'].widget.attrs['class'] = 'form-control w-75 mx-auto'
        users = [('', '')] + list(User.objects.values_list('id', 'username'))
        self.fields['user'] = forms.MultipleChoiceField(choices=users, required=False)
        self.fields['user'].label = 'С кем вы придете? (никнеймы)'
        self.fields['user'].widget.attrs['class'] = 'form-control mx-auto w-75'
        self.fields['additional_info'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['additional_info'].label = 'Дополнительно:'
        self.fields['additional_info'].widget.attrs['class'] = 'textarea form-control mx-auto w-75'
        self.fields['additional_info'].widget.attrs['placeholder'] = 'Пример: мы выбрали время 14:50-18:00, ' \
                                                                     'придем к 16:00'
        self.fields['additional_info'].widget.attrs['rows'] = 3

    class Meta:
        model = SchedulingSystem
        fields = ('time', 'user', 'additional_info')
        # widgets = {'additional_info': TextInput(attrs={'class': 'textarea form-control
        # input-lg w-75 mh-200 mx-auto'})}


class DateChangerForm1(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DateChangerForm1, self).__init__(*args, **kwargs)
        self.fields['day'].label = 'Выберите дату, время на которой Вы хотите изменить:'
        self.fields['day'].widget.attrs['readonly'] = True

    class Meta:
        model = DateChanger
        fields = ('day',)
        widgets = {'day': DateInput(
            attrs={'class': 'datepicker form-control w-50 mx-auto mt-2', 'style': 'background-color: white;'})}

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        if day is None:
            self.add_error('day', forms.ValidationError('Введите дату'))
            return
        if day.weekday() not in [3, 4, 5]:
            self.add_error('day', forms.ValidationError('Некорректная дата'))


class DateChangerForm2(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DateChangerForm2, self).__init__(*args, **kwargs)
        available_time = [('', '')] + [(i.id, i.str_interval) for i in TimeInterval.objects.all()]
        self.fields['available_time'] = forms.MultipleChoiceField(choices=available_time)
        self.fields['available_time'].label = 'Найдите время, которое Вы хотите добавить на дату, или удалите старое:'
        self.fields['available_time'].widget.attrs['class'] = 'form-control mx-auto w-75'

    class Meta:
        model = DateChanger
        fields = ('available_time',)


class TimeIntervalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TimeIntervalForm, self).__init__(*args, **kwargs)
        self.fields['start_time'] = forms.TimeField()
        self.fields['start_time'].label = 'Начало времени:'
        self.fields['end_time'] = forms.TimeField()
        self.fields['end_time'].label = 'Конец времени:'

    class Meta:
        model = TimeInterval
        fields = ('start_time', 'end_time')
