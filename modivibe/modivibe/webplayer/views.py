# Create your views here.
from django.shortcuts import render


def splash(request):
    context = {
        'title': 'Splash'
    }
    return render(request, 'webplayer/splash.html', context)


def home(request):
    context = {
        'title': 'Home'
    }
    return render(request, 'webplayer/home.html', context)


def settings(request):
    context = {
        'title': 'Settings'
    }
    return render(request, 'webplayer/settings.html', context)