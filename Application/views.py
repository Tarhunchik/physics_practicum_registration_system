from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from .models import UserManager, User


def get_context_base():
    context = {
        "title": 'x',
    }
    return context


def index_page(request):
    context = get_context_base()
    context['title'] = 'Main Menu'
    return render(request, 'index.html', context)


def signup_page(request):
    context = get_context_base()
    context['title'] = 'Sign up page'
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            raw_password = request.POST['password1']
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=raw_password
            )
            user.save()
            login(request, user)
            return HttpResponseRedirect('/main')
        else:
            context['registration_form'] = form
    else:
        form = RegisterForm()
        context['form'] = form
    return render(request, 'signup.html', context)


def login_page(request):
    context = get_context_base()
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
