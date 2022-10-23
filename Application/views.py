from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.template import RequestContext
from django.template.loader import get_template
import os
from .forms import RegisterForm, LoginForm, SchSysForm1, SchSysForm2, SchSysForm3
from .models import UserManager, User, SchedulingSystem
from django.contrib import messages
from datetime import date, timedelta
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.db import DataError


def get_context_base():
    context = {
        "title": 'x',
    }
    return context


def index_page(request):
    context = get_context_base()
    context['title'] = 'Главная страница'
    return render(request, 'new_index.html', context)


def register_page(request):
    context = get_context_base()
    context['title'] = 'Регистрация'
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password1']
            grade = request.POST['grade']
            print(grade)
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                grade=grade
            )
            user.save()
            login(request, user)
            return HttpResponseRedirect('/main')
        else:
            context['registration_form'] = form
    else:
        form = RegisterForm()
        context['registration_form'] = form
    return render(request, 'signup.html', context)


def login_page(request):
    context = get_context_base()
    context['title'] = 'Вход в аккаунт'
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/main')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/main')
    else:
        form = LoginForm()
    context['login_form'] = form
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/main')


def test_page(request):
    context = get_context_base()
    context['title'] = 'Задачи'
    if not request.user.is_authenticated:
        context['grade'] = None
    else:
        context['grade'] = request.user.grade
    return render(request, 'new_test.html', context)


def non_authorised_user_page(request):
    context = get_context_base()
    context['title'] = 'Вы не авторизованы'
    return render(request, 'new_non_authorised_user_page.html', context)


def schedule_page1(request):
    context = get_context_base()
    context['title'] = 'Запись'
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/non_auth_user')
    if request.user.is_teacher:
        recs, used, days = [], set(), ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        records = dict()
        for obj in SchedulingSystem.objects.filter(day__gte=date.today()):
            inst_user = User.objects.filter(username=obj.holder).first()
            inst_grade = inst_user.grade
            users = [inst_user] + eval(obj.user)
            people = []
            for i in users:
                user = User.objects.filter(username=i).first()
                people.append(f'{user.first_name} {user.last_name} {user.grade}')
            task_index = int(obj.task)
            time_index = int(obj.time)
            info = obj.additional_info
            day = obj.day
            if inst_grade.startswith('9'):
                tasks = ['Мистер Архимед', 'Для чайников', 'Сопротивление']
            else:
                tasks = ['', '', '', 'Реактивный двигатель', 'Машина Атвуда', 'ДТП']
            records.setdefault(day, [])
            records[day].append([days[obj.day.weekday()],
                                 people,
                                 tasks[task_index - 1],
                                 ['12:00-14:00', '14:00-16:00', '16:00-18:00'][time_index - 1],
                                 info
                                 ])

        records = [list(i) for i in sorted(records.items(), key=lambda x: x[0])]

        for rec in range(len(records)):
            day = str(records[rec][0]).split('-')
            day.reverse()
            records[rec][0] = '.'.join(day)
            records[rec][1].sort(key=lambda x: int(x[3].split(':')[0]))
            records[rec].insert(1, records[rec][1][0])
            records[rec][2] = records[rec][2][1:]
            records[rec].append(len(records[rec][2]) + 1)

        # for ind in range(len(records)):
        #     rec = records[ind]
        #     records[ind] = [rec[0]] + rec[1]

        print(records)
        context['records'] = records
        #     recs.append([obj.holder_name, obj.task, '.'.join(day), days[obj.day.weekday()], obj.time, 'test', obj.additional_info])
        #     used.add(days[obj.day.weekday()])
        # recs = sorted(recs, key=lambda i: (i[2], i[3]))
        # for day in days:
        #     if day not in used:
        #         recs.append(['', '', '', '', day, ''])
        # staff = set()
        # recs = sorted(recs, key=lambda i: (days.index(i[4])))
        # for rec in recs:
        #     if rec[4] in staff:
        #         rec[4] = ''
        #     else:
        #         staff.add(rec[4])
        # context['recs'] = recs
        # context['days'] = days
        # context['used'] = used
        return render(request, 'new_showoff.html', context)
    else:
        if request.user.grade[0] == '9':
            base_choices = [('1', u'Мистер Архимед'), ('2', u'Для чайников'), ('3', u'Сопротивление')]
        else:
            base_choices = [('4', u'Реактивный двигатель'), ('5', u'Машина Атвуда'), ('6', u'ДТП')]
        for task in SchedulingSystem.objects.filter(holder=request.user.username).values_list('task', flat=True):
            i = 0
            while i != len(base_choices):
                if base_choices[i][0] == task:
                    del base_choices[i]
                    i -= 1
                i += 1
        if request.method == 'POST':
            form = SchSysForm1(base_choices, request.POST)
            if form.is_valid():
                inst = form.save(commit=False)
                request.session['task'] = inst.task
                context['href'] = '/main'
                return HttpResponseRedirect('/schedule/2')
        else:
            form = SchSysForm1(base_choices)
        context['scheduling_form'] = form
        context['href'] = '/main'
    return render(request, 'new_schedule.html', context)


def schedule_page2(request):
    context = get_context_base()
    context['title'] = 'Запись'
    response = schedule_page1(request)
    prohibited_days = []
    for day in set(SchedulingSystem.objects.filter(task=request.session.get('task')).values_list('day', flat=True)):
        if len(set(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(day=day).values_list('time',
                                                                                                                 flat=True)).union(
            set(SchedulingSystem.objects.filter(holder=request.user.username).values_list('time',
                                                                                          flat=True)))) == 3:
            prohibited_days.append(str(day))
    if request.method == 'POST':
        form = SchSysForm2(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            request.session['day'] = str(inst.day)
            context['href'] = '/schedule/1'
            return HttpResponseRedirect('/schedule/3')
    else:
        form = SchSysForm2()
    context['scheduling_form'] = form
    context['prohibited_days'] = prohibited_days
    context['href'] = '/schedule/1'
    return render(request, 'new_schedule.html', context)


def schedule_page3(request):
    context = get_context_base()
    context['title'] = 'Запись'
    base_choices = []
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 3:
        base_choices = [('1', u'16:45 — 19:00')]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 4:
        base_choices = [('1', u'14:50 — 17:00')]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 5:
        base_choices = [('1', u'8:30 — 10:15'), ('2', u'10:35 — 12:25'), ('3', u'14:50 — 18:00')]
    prohibited_time = []
    for time in set(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(
            day=request.session.get('day')).values_list('time', flat=True)).union(
        set(SchedulingSystem.objects.filter(holder=request.user.username).values_list('time', flat=True))):
        prohibited_time.append(time)
        print(time)
    i = 0
    while i != len(base_choices):
        if base_choices[i][0] in prohibited_time:
            del base_choices[i]
            i -= 1
        i += 1
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        term = request.GET.get('term')
        if term:
            users = User.objects.all().filter(username__icontains=term).filter(is_teacher=False).filter(
                Q(grade=request.user.grade[0] + '-6') | Q(grade=request.user.grade[0] + '-7') | Q(
                    grade=request.user.grade[0] + '0-6') | Q(grade=request.user.grade[0] + '0-7')).filter(
                ~Q(username=request.user.username))
            return JsonResponse(list(users.values()), safe=False)
    if request.method == 'POST':
        form = SchSysForm3(base_choices, request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.user = '[' + ', '.join(
                ['"' + User.objects.get(id=i).username + '"' for i in eval(inst.user or '[]')]) + ']'
            inst.task = request.session.get('task')
            inst.day = request.session.get('day')
            inst.holder = request.user.username
            inst.holder_name = f'{request.user.first_name} {request.user.last_name}'
            inst.save()
            context['href'] = '/schedule/2'
            messages.success(request, 'Запись прошла успешно. Проверьте свой личный кабинет')
            return render(request, 'new_index.html', context)
    else:
        form = SchSysForm3(choices=base_choices)
    context['scheduling_form'] = form
    context['href'] = '/schedule/2'
    return render(request, 'new_schedule.html', context)


def tg_bot_page(request):
    context = get_context_base()
    context['title'] = 'Телеграм бот'
    return render(request, 'new_telegram_bot.html', context)


def contacts_page(request):
    context = get_context_base()
    context['title'] = 'Наши контакты'
    return render(request, 'new_contacts.html', context)


def account_page(request):
    context = get_context_base()
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/non_auth_user')
    cur_recs = []
    for obj in SchedulingSystem.objects.filter(day__gte=date.today()):
        if obj.holder == request.user.username:
            task = ['Мистер Архимед', 'Для чайников', 'Сопротивление',
                    'Реактивный двигатель', 'Машина Атвуда', 'ДТП'][int(obj.task) - 1]
            time = ['12:00 - 14:00', '14:00 - 16:00', '16:00 - 18:00'][int(obj.time) - 1]
            day = str(obj.day).split('-')
            day.reverse()
            cur_recs.append((task, time, '.'.join(day), obj.id, obj.additional_info))
    if request.method == 'POST':
        for rec in cur_recs:
            if str(rec[3]) in request.POST:
                SchedulingSystem.objects.filter(id=rec[3]).delete()
        return HttpResponseRedirect('/account')
    else:
        past_recs = []
        for obj in SchedulingSystem.objects.filter(day__lte=date.today()):
            if obj.holder == request.user.username:
                task = ['Мистер Архимед', 'Для чайников', 'Сопротивление',
                        'Реактивный двигатель', 'Машина Атвуда', 'ДТП'][int(obj.task) - 1]
                time = ['12:00 - 14:00', '14:00 - 16:00', '16:00 - 18:00'][int(obj.time) - 1]
                day = str(obj.day).split('-')
                day.reverse()
                past_recs.append((task, time, '.'.join(day), obj.additional_info))
        other_recs = []
        for obj in SchedulingSystem.objects.all():
            if request.user.username in eval(obj.user):
                task = ['Мистер Архимед', 'Для чайников', 'Сопротивление',
                        'Реактивный двигатель', 'Машина Атвуда', 'ДТП'][int(obj.task) - 1]
                time = ['12:00 - 14:00', '14:00 - 16:00', '16:00 - 18:00'][int(obj.time) - 1]
                day = str(obj.day).split('-')
                day.reverse()
                other_recs.append((task, time, '.'.join(day), obj.id, obj.additional_info))
        context['title'] = f'{request.user.username} аккаунт'
        context['name'] = request.user.username
        context['teacher'] = request.user.is_teacher
        context['admin'] = request.user.is_admin
        context['class'] = request.user.grade
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        context['cur_recs'] = cur_recs
        print(other_recs)
        context['other_recs'] = other_recs
        context['past_recs'] = past_recs
        return render(request, 'new_account.html', context)


def error_404(request, exception):
    return render(request, 'error_404.html')


def error_500(request):
    return render(request, 'error_500.html')


def rules_page(request):
    context = get_context_base()
    context['title'] = 'Правила и прочее'
    return render(request, 'rules.html', context)
