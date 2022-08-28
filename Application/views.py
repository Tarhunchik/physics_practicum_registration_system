from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm, SchedulingSystemForm
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
    if request.POST:
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


def schedule_page(request):
    context = get_context_base()
    context['title'] = 'Schedule page'
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/non_auth_user')
    if request.user.is_role_teacher():
        arr = []
        for obj in SchedulingSystem.objects.filter(day__gte=date.today()):
            obj_holder = getattr(obj, 'holder_name')
            obj_task = getattr(obj, 'task')
            obj_day = getattr(obj, 'day')
            obj_time = getattr(obj, 'time')
            arr.append((obj_day, obj_time, obj_holder, obj_task))
        arr = sorted(arr, key=lambda i: (i[0], i[1]))
        context['content'] = [f'{i[2]}: {i[0]} {["12:00 - 14:00", "14:00 - 16:00", "16:00 - 18:00"][int(i[1]) - 1]}, {["task 1", "task 2", "task 3"][int(i[3]) - 1]}' for i in arr]
        return render(request, 'showoff.html', context)
    else:
        if request.POST:
            form = SchedulingSystemForm(request.POST)
            print(form)
            if form.is_valid():
                object_instance = form.save(commit=False)
                for obj in SchedulingSystem.objects.all():
                    inst_task = getattr(object_instance, 'task')
                    inst_day = getattr(object_instance, 'day')
                    inst_time = getattr(object_instance, 'time')
                    obj_task = getattr(obj, 'task')
                    obj_day = getattr(obj, 'day')
                    obj_time = getattr(obj, 'time')
                    obj_holder = getattr(obj, 'holder')
                    print(request.user.get_username, obj_holder)
                    print(inst_task, obj_task)
                    if request.user.get_username() == obj_holder and inst_task == obj_task:
                        messages.error(request, 'ВНИМАНИЕ! Нельзя записываться на одну и ту же задачу дважды')
                        return HttpResponseRedirect('/schedule')
                    if inst_task == obj_task and inst_day == obj_day and inst_time == obj_time:
                        messages.error(request, 'ВНИМАНИЕ! Запись занята. Попробуйте еще раз')
                        return HttpResponseRedirect('/schedule')
                object_instance.holder = request.user.get_username()
                object_instance.holder_name = request.user.get_full_name()
                form.save()
                messages.success(request, 'Запись прошла успешно')
                return HttpResponseRedirect('/schedule')
        else:
            form = SchedulingSystemForm()
        context['scheduling_form'] = form
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

