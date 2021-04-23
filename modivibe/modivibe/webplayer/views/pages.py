# All views here will be dedicated to rendering page content
from django.http import HttpResponse
from django.shortcuts import render, redirect
from webplayer.SpotifyApiObjs import sp, auth_manager
from spotipy.oauth2 import SpotifyOauthError


# Login flow: splash, click loginurl -> redirectToHome -> splash or home
def splash(request):
    context = {
        'title': 'Splash',
        'loginurl': auth_manager.get_authorize_url()
    }
    return render(request, 'webplayer/splash.html', context)


def home(request):
    try:
        userAccessCode = auth_manager.get_access_token().get('access_token')
    except:
        return redirect('splash')

    context = {
        'title': 'Home',
        'userAccessCode': userAccessCode
    }
    return render(request, 'webplayer/home.html', context)

