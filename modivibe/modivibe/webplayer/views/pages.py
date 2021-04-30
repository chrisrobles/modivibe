# All views here will be dedicated to rendering page content
from django.http import HttpResponse
from django.shortcuts import render, redirect
from webplayer.SpotifyApiObjs import sp, auth_manager
from spotipy.oauth2 import SpotifyOauthError
from webplayer.views.spotipy_api import validUser, isAjaxRequest
from django.http import JsonResponse
from django.template.loader import render_to_string



# Login flow: splash, click loginurl -> redirectToHome -> splash or home
def splash(request):
    context = {
        'title': 'Splash',
        'loginurl': auth_manager.get_authorize_url()
    }
    return render(request, 'webplayer/splash.html', context)


def home(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')
    try:
        userAccessCode = auth_manager.get_access_token().get('access_token')
    except:
        return redirect('splash')

    context = {
        'title': 'Home',
        'userAccessCode': userAccessCode
    }

    if isAjaxRequest(request):
        context['ajax'] = True
        page = render_to_string('webplayer/home.html', context=context)
        return JsonResponse({"collection": page, 'status': 200 })
    else:
        context['ajax'] = False
        return render(request, 'webplayer/home.html', context=context)

    #return render(request, 'webplayer/home.html', context)

