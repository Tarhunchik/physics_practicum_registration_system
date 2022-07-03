from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import RegisterForm
from .models import UserManager


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
    context['form'] = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            UserManager.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['username'],
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name'],
                form.cleaned_data['password']
            )
        return HttpResponseRedirect('/main/')
    else:
        return render(request, 'signup.html', context)


def test_page(request):
    context = get_context_base()
    context['title'] = 'Test page'
    return render(request, 'test.html', context)
