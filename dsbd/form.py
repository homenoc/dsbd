from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django import forms

from custom_auth.models import User


class LoginForm(AuthenticationForm):
    token = forms.CharField(label="token", max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class OTPForm(forms.Form):
    token = forms.CharField(label="token", max_length=150, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class AuthTOTP(forms.Form):
    token = forms.IntegerField(label="totp", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class ForgetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class NewSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class SignUpForm(forms.Form):
    username = forms.CharField(label="ユーザネーム(english)", max_length=150, required=True)
    username_jp = forms.CharField(label="ユーザネーム(japanese)", max_length=150, required=True)
    display_name = forms.CharField(label="display_name", max_length=150, required=True)
    email = forms.EmailField(label="email", max_length=150, required=True)
    password1 = forms.CharField(label="password", widget=forms.PasswordInput(), min_length=8)
    password2 = forms.CharField(label="password(確認用)", widget=forms.PasswordInput(), min_length=8)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("パスワードが一致しません")

    def create_user(self):
        User.objects.create_user(
            username=self.cleaned_data["username"],
            username_jp=self.cleaned_data["username_jp"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
        )