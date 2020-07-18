from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from accounts.models import Profile


def log_in(request):
    template_name = 'accounts/login.html'
    if request.method == 'POST':
        username = request.POST['username']
        psw = request.POST['psw']
        context = {
            'username': username,
            'psw': psw
        }
        # check username validity
        user = User.objects.filter(username=username)
        if not user.exists():
            context["invalid"] = "username"
            return render(request, template_name, context)
        username = user.first().username
        user = authenticate(username=username, password=psw)
        if user is not None:
            login(request, user)
            request.session['id'] = user.id
            profile = Profile.objects.get(user=user)
            try:
                photo_url = profile.photo.url
                request.session['photo_url'] = photo_url
            except Exception as err:
                print(str(err))
                request.session['photo_url'] = 'images/default.png'
            return redirect('home:home')
        else:
            context["invalid"] = "psw"
            return render(request, template_name, context)
    return render(request, template_name)


def log_out(request):
    logout(request)
    return redirect('home:home')
