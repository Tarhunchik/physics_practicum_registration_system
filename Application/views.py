from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm, SchSysForm1, SchSysForm2, SchSysForm3
from .models import UserManager, User, SchedulingSystem
from django.contrib import messages
from datetime import date


def get_context_base():
    context = {
        "title": 'x',
    }
    return context


def index_page(request):
    context = get_context_base()
    context['title'] = 'Main Menu'
    return render(request, 'index.html', context)


def register_page(request):
    context = get_context_base()
    context['title'] = 'Sign up page'
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password1
                )
                user.save()
                # messages.success(request, 'User created successfully')
                login(request, user)
                return HttpResponseRedirect('/main')
            messages.error(request, 'Passwords are not same')
        else:
            messages.error(request, 'Input data is not valid')
            context['registration_form'] = form
    else:
        form = RegisterForm()
        context['registration_form'] = form
    return render(request, 'signup.html', context)


def login_page(request):
    context = get_context_base()
    context['title'] = 'Login page'
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
    context['title'] = 'Test page'
    return render(request, 'test.html', context)


def non_authorised_user_page(request):
    context = get_context_base()
    context['title'] = 'Authorise now!'
    return render(request, 'non_authorised_user_page.html', context)


def schedule_page1(request):
    context = get_context_base()
    context['title'] = 'Schedule page'
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/non_auth_user')
    if request.user.is_teacher:
        recs = []
        for obj in SchedulingSystem.objects.filter(day__gte=date.today()):
            recs.append((obj.holder_name, obj.task, obj.day, obj.time, obj.additional_info))
        context['recs'] = sorted(recs, key=lambda i: (i[0], i[1]))
        return render(request, 'showoff.html', context)
    else:
        base_choices = [('1', u'task 1'), ('2', u'task 2'), ('3', u'task 3')]
        if request.method == 'POST':
            form = SchSysForm1(base_choices, request.POST)
            if form.is_valid():
                inst = form.save(commit=False)
                prohibited_days = []
                for day in set(SchedulingSystem.objects.filter(task=inst.task).values_list('day', flat=True)):
                    if len(SchedulingSystem.objects.filter(task=inst.task).filter(day=day)) == 3:
                        prohibited_days.append(day)
                task = inst.task
                request.session['task'] = task
                request.session['prohibited_days'] = [str(i) for i in prohibited_days]
                return HttpResponseRedirect('/schedule/2')
        else:
            for task in SchedulingSystem.objects.filter(holder=request.user.username).values_list('task', flat=True):
                i = 0
                while i != len(base_choices):
                    if base_choices[i][0] == task:
                        del base_choices[i]
                        i -= 1
                    i += 1
            form = SchSysForm1(base_choices)
        context['scheduling_form'] = form
        context['href'] = '/main'
    return render(request, 'schedule.html', context)


def schedule_page2(request):
    context = get_context_base()
    response = schedule_page1(request)
    if request.method == 'POST':
        form = SchSysForm2(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            prohibited_time = []
            for time in set(SchedulingSystem.objects.filter(task=request.session.get('task')).filter(day=inst.day).values_list('time', flat=True)):
                prohibited_time.append(time)
            request.session['prohibited_time'] = prohibited_time
            request.session['day'] = str(inst.day)
            return HttpResponseRedirect('/schedule/3')
    else:
        form = SchSysForm2()
    context['scheduling_form'] = form
    context['prohibited_days'] = request.session.get('prohibited_days')
    context['href'] = '/schedule/1'
    return render(request, 'schedule.html', context)


def schedule_page3(request):
    context = get_context_base()
    response = schedule_page2(request)
    base_choices = [('1', u'12:00 - 14:00'), ('2', u'14:00 - 16:00'), ('3', u'16:00 - 18:00')]
    if request.method == 'POST':
        form = SchSysForm3(base_choices, request.POST)
        print(form.is_valid())
        print('error has been here')
        if form.is_valid():
            inst = form.save(commit=False)
            inst.task = request.session.get('task')
            inst.day = request.session.get('day')
            inst.holder = request.user.username
            inst.holder_name = f'{request.user.first_name} {request.user.last_name}'
            inst.save()
            messages.success(request, 'Запись прошла успешно')
            return HttpResponseRedirect('/main')
    else:
        i = 0
        while i != len(base_choices):
            if base_choices[i][0] in request.session.get('prohibited_time'):
                del base_choices[i]
                i -= 1
            i += 1
        print(base_choices)
        form = SchSysForm3(choices=base_choices)
    context['scheduling_form'] = form
    context['href'] = '/schedule/2'
    return render(request, 'schedule.html', context)


def tg_bot_page(request):
    context = get_context_base()
    context['title'] = 'Telegram bot page'
    return render(request, 'telegram_bot.html', context)


def contacts_page(request):
    context = get_context_base()
    context['title'] = 'Contacts page'
    return render(request, 'contacts.html', context)


def rules_page(request):
    context = get_context_base()
    context['title'] = 'Rules page'
    return render(request, 'rules.html', context)


def recording_success_page(request):
    context = get_context_base()
    context['title'] = 'Congratulations!'
    return render(request, 'recording_done_successfully.html', context)


def recording_error_page(request):
    context = get_context_base()
    context['title'] = 'Recoding error page'
    return render(request, 'recording_is_busy.html', context)


def account_page(request):
    context = get_context_base()
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/non_auth_user')
    cur_recs = []
    for obj in SchedulingSystem.objects.filter(day__gte=date.today()):
        if obj.holder == request.user.username:
            task = ['task 1', 'task 2', 'task 3'][int(obj.task) - 1]
            time = ['12:00 - 14:00', '14:00 - 16:00', '16:00 - 18:00'][int(obj.time) - 1]
            cur_recs.append((task, obj.day, time, obj.id))
    if request.method == 'POST':
        for rec in cur_recs:
            if str(rec[3]) in request.POST:
                SchedulingSystem.objects.filter(id=rec[3]).delete()
        return HttpResponseRedirect('/account')
    else:
        past_recs = []
        for obj in SchedulingSystem.objects.filter(day__lt=date.today()):
            if obj.holder == request.user.username:
                task = ['task 1', 'task 2', 'task 3'][int(obj.task) - 1]
                time = ['12:00 - 14:00', '14:00 - 16:00', '16:00 - 18:00'][int(obj.time) - 1]
                past_recs.append((task, obj.day, time))
        context['title'] = f'{request.user.username} account'
        context['name'] = request.user.username
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        cur_recs.reverse()
        context['cur_recs'] = cur_recs
        context['past_recs'] = past_recs
        return render(request, 'account.html', context)

