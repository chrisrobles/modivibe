# Create your views here.
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
    # this just checks that the api is working for you, delete when ready
    print(sp.current_user())

    context = {
        'title': 'Home'
    }
    return render(request, 'webplayer/home.html', context)

# After logging in, we're redirected to this redirect uri
# Verifies that a valid code is given and redirects user to proper page
# Does not require an html page
def redirectToHome(request):

    # redirect if a code is not given
    if 'code' not in request.GET:
        return redirect('splash') # will redirect to splash

    # validate the code given
    try:
        # Check_cache may have to be changed later depending on how we handle caching
        api_token = auth_manager.get_access_token(request.GET['code'], check_cache=False)
    except SpotifyOauthError:
        # if a code is not valid, a SpotifyOauthError is thrown
        return redirect('splash') # redirect to splash

    # Token will be stored in a .cache file, can also uncomment line below to verify
    # Be sure to delete token in .cache when done
    # print(api_token)

    # valid token is obtained
    return redirect('webplayer')

def settings(request):
    context = {
        'title': 'Settings'
    }
    return render(request, 'webplayer/settings.html', context)