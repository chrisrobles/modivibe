from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from modivibe.webplayer.SpotifyApiObjs import sp, auth_manager

def index(request):
    return render(request, 'webplayer/index.html')

def settings(request):
    return render(request, 'webplayer/settings.html')