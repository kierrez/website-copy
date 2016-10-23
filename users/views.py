from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from .forms import RegisterForm, LoginForm, EditProfileForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import UserProfile

def register(request):
    form_data = request.POST if request.method == 'POST' else None
    form = RegisterForm(form_data)
    if form.is_valid():
        user = form.save()
        user.set_password(user.password)
        user.save()
        profile = UserProfile()
        profile.user = user
        profile.save()
        message = 'Successful registration'
        if request.POST.get('login_after') == 'on':
            created_user = auth.authenticate(username=user.username, password=request.POST.get('password'))
            auth.login(request, created_user)
            message += '. You have been logged in'
        messages.success(request, '{}, {}'.format(message, user.username), extra_tags='alert-success')
        return redirect(reverse('home'))
    return render(request, 'users/register.html', {'form': form})


def login(request):
    form_data = request.POST if request.method == 'POST' else None
    form = LoginForm(form_data)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                messages.success(request, 'You have been logged in: ' + user.username, extra_tags='alert-success')
                return redirect(reverse('home'))
            else:
                messages.error(request, 'User not active', extra_tags='alert-warning')
        else:
            messages.error(request, 'Invalid creditentials', extra_tags='alert-warning')
    context = {
        'form': form,
        'title': 'login'
    }
    return render(request, 'users/login.html', context)

# @login_required
def user_edit(request, username):
    # requested_obj = get_object_or_404(User, username=username)
    # form = EditProfileForm(instance=UserProfile.objects.get(user__username=username))
    # form_data = request.POST if request.method == 'POST' else None
    # if form_data.is_valid():
    profile = UserProfile.objects.get(user__username=username)
    form = EditProfileForm(instance=profile)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
        'title': 'profile edit'
    }
    return render(request, 'users/profile_edit.html', context)


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out: ' + request.user.username, extra_tags='alert-success')
    return redirect(request.META.get('HTTP_REFERER'))


def user_list(request):
    context = {
        'title': 'User list',
        'user_list': User.objects.all(),
    }
    return render(request, 'users/user_list.html', context)


def user_profile(request, username):
    requested_obj = get_object_or_404(User, username=username)
    context = {
        'title': 'User profile: ' + requested_obj.username,
        'user': requested_obj,
    }
    return render(request, 'users/user_profile.html', context)