from django.contrib.auth import logout, get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages

from sitetour.models import Tour, Booking
from .forms import RegisterUserForm

from .forms import UserPasswordChangeForm
from users.forms import RegisterUserForm, LoginUserForm, ProfileUserForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация',
                     'static_root': "users/css/login-register.css",
                     }

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация',
                     'static_root': "users/css/login-register.css",
                     }
    success_url = reverse_lazy('users:login')


class ProfileUserView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'

    extra_context = {
        'title': "Профиль пользователя",
        'static_root': "users/css/profile.css",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        context['user'] = user
        context['orders'] = Booking.objects.filter(Q(user_id=user,status=Booking.PAID))
        return context


    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'
    extra_context = {
        'title': "Смена пароля",
        'static_root': "users/css/login-register.css",
    }

class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
    extra_context={'title':'Успех','static_root': "css/base.css"}


class LoginRegisterView(View):
    template_name = 'users/login_register.html'
    login_form_class = LoginUserForm
    register_form_class = RegisterUserForm

    def get(self, request, *args, **kwargs):
        # Отображаем пустые формы при GET-запросе
        login_form = self.login_form_class()
        register_form = self.register_form_class()
        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form,
            'static_root': "users/css/login-register.css",
        })

    def post(self, request, *args, **kwargs):
        login_form = self.login_form_class(data=request.POST, prefix='login')  # Добавьте prefix
        register_form = self.register_form_class(data=request.POST, files=request.FILES, prefix='register')

        if 'login' in request.POST:
            if login_form.is_valid():  # Бэкенды автоматически вызовутся здесь
                user = login_form.get_user()
                auth_login(request, user)
                messages.success(request, 'Вы успешно вошли!')
                return redirect('home')
            else:
                messages.error(request, 'Ошибка входа')

        elif 'register' in request.POST:
            if register_form.is_valid():
                register_form.save()
                messages.success(request, 'Регистрация успешна!')
                return redirect('login_register')
            else:
                messages.error(request, 'Ошибка регистрации')

        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form,
            'static_root': "users/css/login-register.css",
        })


class VkAuthView(TemplateView):
    template_name = 'users/vk_auth.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Авторизация ВК'
        return context