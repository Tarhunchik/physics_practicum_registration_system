from django import forms
from .models import User
from django.contrib.auth import authenticate


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        help_text="Required. Type your username",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'username',
            }
        )
    )
    first_name = forms.CharField(
        max_length=20,
        help_text="Required. Type your first name",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'first_name',
            }
        )
    )
    last_name = forms.CharField(
        max_length=20,
        help_text="Required. Type your last name",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'last_name',
            }
        )
    )
    email = forms.EmailField(
        max_length=60,
        help_text="Required. Add a valid email address",
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'email',
            }
        )
    )
    password1 = forms.CharField(
        max_length=20,
        help_text="Required. Type your password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password',
            }
        )
    )
    password2 = forms.CharField(
        max_length=20,
        help_text="Required. Type your password again",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password',
            }
        )
    )

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")


class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not authenticate(username=username, password=password):
            raise forms.ValidationError('Invalid login')
