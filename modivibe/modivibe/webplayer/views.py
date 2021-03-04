from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


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