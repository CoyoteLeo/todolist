from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
# todo login required class-based view
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.conf import settings
from .form import UserForm, UserCreateForm, PasswordResetRequestForm, UserPasswordResetForm, UserPasswordChangeForm
from .models import Profile
import json

UserModel = get_user_model()


class HttpBase(object):
    http_method_names = ['get', 'post']

    @staticmethod
    def redirect(request, target):
        return HttpResponseRedirect(request.GET['next']) if "next" in request.GET else redirect(target)


class Login(View, HttpBase):
    # todo 輸入信箱 寄送認證信
    context = {"header": "登入 Login"}

    def __init__(self):
        self.context = {}
        super(Login, self).__init__()

    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect(request=request, target=reverse("index"))
        else:
            return self._common_task(request)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return self.redirect(request=request, target=reverse('index'))
        else:
            self.context["error_message"] = "帳號或密碼錯誤，請重新輸入"
            return self._common_task(request)

    def _common_task(self, request):
        return render(request, "user/login.html", self.context)


def logout_action(request):
    logout(request)
    return redirect(reverse('index'))


class Register(View, HttpBase):
    def __init__(self):
        self.context = {}
        super(Register, self).__init__()

    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect(request=request, target=reverse("user:profile"))
        self.context["form"] = UserCreateForm()
        return self._common_task(request)

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            return redirect(reverse('user:login'))
        error_message = ""
        errors = json.loads(form.errors.as_json())
        for error in errors:
            for tmp in errors[error]:
                error_message += tmp['message'] + "\n"
        self.context["form"] = form
        self.context["error_message"] = error_message
        return self._common_task(request)

    def _common_task(self, request):
        return render(request, 'user/register.html', self.context)


class ProfileView(LoginRequiredMixin, View, HttpBase):
    login_url = "/user/login"

    def __init__(self):
        self.context = {}
        super(ProfileView, self).__init__()

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        self.context['form'] = UserForm(instance=user)
        return self._common_task(request=request)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        form = UserForm(request.POST, instance=user)
        print(form.data)
        if form.is_valid():
            if user.check_password(form.cleaned_data['password']):
                form.save()
            else:
                self.context["error_message"] = "密碼錯誤！請再次確認"
        else:
            error_message = ""
            errors = json.loads(form.errors.as_json())
            print(errors)
            for error in errors:
                for tmp in errors[error]:
                    error_message += tmp['message'] + "\n"
            self.context["error_message"] = error_message
        return self.get(request)

    def _common_task(self, request):
        return render(request, 'user/profile.html', self.context)


class PasswordChange(LoginRequiredMixin, View, HttpBase):
    def __init__(self):
        self.context = {}
        super(PasswordChange, self).__init__()

    def get(self, request):
        self.context['form'] = UserPasswordChangeForm
        return render(request, "user/password_change_form.html", self.context)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        print(request.POST)
        form = UserPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            return render(request, 'user/password_change_done.html', self.context)
        else:
            error_message = ""
            errors = json.loads(form.errors.as_json())
            print(errors)
            for error in errors:
                for tmp in errors[error]:
                    error_message += tmp['message'] + "\n"
            self.context["error_message"] = error_message
        return self.get(request)


class PasswordReset(object):
    class Request(View, HttpBase):

        def __init__(self):
            self.context = {}
            super(View, self).__init__()

        def get(self, request):
            if request.user.is_authenticated:
                return self.redirect(request=request, target=reverse("index"))
            else:
                return render(request, "user/password_reset_request.html", self.context)

        def post(self, request):
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                # todo password reset form 可在 form.py 繼承django預設並對其進行客製(email內容等等)
                form.save(request=request, email_template_name="user/password_reset_email.html",
                          use_https=request.is_secure(), domain_override=settings.HOST)
                '''
                from django.contrib.sites.shortcuts import get_current_site
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                site_name = domain = domain_override
                from django.contrib.auth.tokens import default_token_generator
                token= default_token_generator.make_token(user),
                protocol='https' if request.is_secure() else 'http',
                '''
                # todo: special: need to pass some parameters to method
                return render(request, "user/password_reset_send_email.html", self.context)
            else:
                error_message = ""
                errors = json.loads(form.errors.as_json())
                print(errors)
                for error in errors:
                    for tmp in errors[error]:
                        error_message += tmp['message'] + "\n"
                return render(request, "user/password_reset_request.html", self.context)

    class Form(View, HttpBase):

        def __init__(self):
            self.context = {}
            super(View, self).__init__()

        def __check_idenity(self, uidb64=None, token=None):
            if uidb64 is not None and token is not None:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = UserModel._default_manager.get(pk=uid)
                if user is not None and default_token_generator.check_token(user, token):
                    self.context['validlink'] = True
                    return user
            return None

        def get(self, request, uidb64=None, token=None):
            if request.user.is_authenticated:
                return self.redirect(request=request, target=reverse("index"))
            else:
                user = self.__check_idenity(uidb64=uidb64, token=token)
                if user is None:
                    return redirect(reverse("index"))
                # form = UserPasswordResetForm(user)
                return render(request, "user/password_reset_form.html", self.context)

        def post(self, request, uidb64=None, token=None):
            if request.user.is_authenticated:
                return self.redirect(request=request, target=reverse("index"))
            else:
                user = self.__check_idenity(uidb64=uidb64, token=token)
                if user is not None:
                    form = UserPasswordResetForm(user, request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse("user:profile"))
                    return self.get(request=request, uidb64=uidb64, token=token)
                else:
                    return redirect(reverse("index"))


def index(request):
    return render(request, 'index.html', locals())
