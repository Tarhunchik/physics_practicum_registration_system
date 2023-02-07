from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm, SchSysForm1, SchSysForm2, SchSysForm3, DateChangerForm1, DateChangerForm2, \
    TimeIntervalForm
from .models import User, SchedulingSystem, DateChanger, TimeInterval
from django.contrib import messages
from datetime import date
from django.http import JsonResponse
from django.db.models import Q


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
            records[day].append(
                [days[obj.day.weekday()], people, tasks[task_index - 1], TimeInterval.objects.filter(pk=time_index)[0].str_interval, info])

        records = [list(i) for i in sorted(records.items(), key=lambda x: x[0])]

        for rec in range(len(records)):
            day = str(records[rec][0]).split('-')
            day.reverse()
            records[rec][0] = '.'.join(day)
            records[rec][1].sort(key=lambda x: int(x[3].split(':')[0]))
            records[rec].insert(1, records[rec][1][0])
            records[rec][2] = records[rec][2][1:]
            records[rec].append(len(records[rec][2]) + 1)
        context['records'] = records
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
    prohibited_days = []
    for day in set(SchedulingSystem.objects.values_list('day', flat=True)):
        if len(DateChanger.objects.filter(day=day)):
            if len(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(day=day)) + len(SchedulingSystem.objects.filter(holder=request.user.username).filter(day=request.session.get('day'))) >= len(eval(DateChanger.objects.filter(day=day).values_list('available_time')[0][0])):
                prohibited_days.append(str(day))
        else:
            if len(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(day=day)) + len(SchedulingSystem.objects.filter(holder=request.user.username).filter(day=request.session.get('day'))) >= [1, 1, 3][day.weekday() - 3]:
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
        base_choices = [(1, TimeInterval.objects.get(pk=1).str_interval)]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 4:
        base_choices = [(2, TimeInterval.objects.get(pk=2).str_interval)]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 5:
        base_choices = [(3, TimeInterval.objects.get(pk=3).str_interval), (4, TimeInterval.objects.get(pk=4).str_interval), (5, TimeInterval.objects.get(pk=5).str_interval)]
    if DateChanger.objects.filter(day=request.session.get('day')):
        time_id = eval(DateChanger.objects.filter(day=request.session.get('day')).values_list('available_time')[0][0])
        base_choices = [(i, TimeInterval.objects.get(pk=i).str_interval) for i in time_id]
    prohibited_time = []
    for time in set(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(day=request.session.get('day')).values_list('time', flat=True)).union(set(SchedulingSystem.objects.filter(holder=request.user.username).filter(day=request.session.get('day')).values_list('time', flat=True))):
        prohibited_time.append(int(time))
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
                Q(grade=request.user.grade[0] + '-5') | Q(grade=request.user.grade[0] + '-6') | Q(
                    grade=request.user.grade[0] + '-7') | Q(grade=request.user.grade[0] + '-9') | Q(
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


def date_changer_page1(request):
    context = get_context_base()
    context['title'] = 'Изменение записи'

    if request.method == 'POST':
        form = DateChangerForm1(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            request.session['day'] = str(inst.day)
            context['href'] = '/schedule/1'
            return HttpResponseRedirect('/reschedule/2')
    else:
        form = DateChangerForm1()

    context['scheduling_form'] = form
    context['href'] = '/schedule/1'
    return render(request, 'reschedule.html', context)


def date_changer_page2(request):
    context = get_context_base()
    context['title'] = 'Изменение записи'
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        term = request.GET.get('term')
        if term:
            available_time = [(i.id, i.str_interval) for i in TimeInterval.objects.filter(str_interval__contains=term)]
            return JsonResponse(available_time, safe=False)
    if request.method == 'POST':
        if len(DateChanger.objects.filter(day=request.session.get('day'))):
            form = DateChangerForm2(request.POST, instance=DateChanger.objects.filter(day=request.session.get('day'))[0])
        else:
            form = DateChangerForm2(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.day = request.session.get('day')
            inst.available_time = '[' + ', '.join([i for i in eval(inst.available_time or '[]')]) + ']'
            inst.save()
            context['href'] = '/schedule/2'
            return render(request, 'new_index.html', context)
    else:
        form = DateChangerForm2()
    active_time = []
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 3:
        active_time = [1]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 4:
        active_time = [2]
    if date(*map(int, request.session.get('day').split('-'))).weekday() == 5:
        active_time = [3, 4, 5]
    if DateChanger.objects.filter(day=request.session.get('day')):
        time_id = eval(DateChanger.objects.filter(day=request.session.get('day')).values_list('available_time')[0][0])
        active_time = [i for i in time_id]
    context['scheduling_form'] = form
    context['active_time'] = active_time
    context['href'] = '/schedule/2'
    return render(request, 'reschedule.html', context)


def new_time_interval(request):
    context = get_context_base()
    context['title'] = 'Добавление нового интервала'
    if request.method == 'POST':
        form = TimeIntervalForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.str_interval = f'{str(inst.start_time)[:-3]} — {str(inst.end_time)[:-3]}'
            inst.save()
            return render(request, 'new_index.html', context)
    else:
        form = TimeIntervalForm()
    context['scheduling_form'] = form
    return render(request, 'time_interval.html', context)


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
            print("TRACE: obj.time", obj.time)
            time = TimeInterval.objects.filter(pk=obj.time)[0].str_interval
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
                time = TimeInterval.objects.filter(pk=obj.time)[0].str_interval
                day = str(obj.day).split('-')
                day.reverse()
                past_recs.append((task, time, '.'.join(day), obj.additional_info))
        other_recs = []
        for obj in SchedulingSystem.objects.all():
            if request.user.username in eval(obj.user):
                task = ['Мистер Архимед', 'Для чайников', 'Сопротивление',
                        'Реактивный двигатель', 'Машина Атвуда', 'ДТП'][int(obj.task) - 1]
                time = TimeInterval.objects.filter(pk=obj.time)[0].str_interval
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
        context['other_recs'] = other_recs
        context['other_recs'] = other_recs
        context['past_recs'] = past_recs
        return render(request, 'new_account.html', context)


def records_rules_page(request):
    context = get_context_base()
    context['title'] = 'Как записываться?'
    return render(request, 'record_rules.html', context)


def error_404(request, exception):
    return render(request, 'error_404.html')


def error_500(request):
    return render(request, 'error_500.html')


def rules_page(request):
    context = get_context_base()
    context['title'] = 'Правила и прочее'
    return render(request, 'rules.html', context)
