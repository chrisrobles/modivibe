# All views here will be dedicated to API calls
from django.http import HttpResponse
from django.shortcuts import render, redirect
from ..SpotifyApiObjs import sp, auth_manager
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError


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


# Sets Spotify's active device to Modivibe
# Expects:
#   device_id [STRING] (generated device id)
def transferPlayback(request):
    response = False
    deviceID = request.POST['device_id']
    try:
        sp.transfer_playback(deviceID, force_play=False)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Resumes or pauses playback for a specific device
# Expects:
#   device_id [STRING] (generated device id)
#   status [STRING] ('play' || 'pause')
def setPlayback(request):
    response = False
    deviceID = request.POST['device_id']
    songStatus = request.POST['status']
    try:
        # Temporarily attempt to ensure Modivibe becomes the active device
        sp.transfer_playback(deviceID, force_play=False)
        if songStatus == 'play':
            sp.start_playback(device_id=deviceID)
            response = True
        elif songStatus == 'pause':
            sp.pause_playback(device_id=deviceID)
            response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Sets volume for a specific device
# Expects:
#   device_id [STRING] (generated device id)
#   volume [STRING||INT] (value checked from 0-100 by spotipy)
def setVolume(request):
    response = False
    deviceID = request.POST['device_id']
    songVolume = int(request.POST['volume'])
    try:
        sp.volume(volume_percent=songVolume, device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Skips to next track in user's queue
# Excepts:
#   device_id [STRING] (generated device id)
def nextTrack(request):
    response = False
    deviceID = request.POST['device_id']
    try:
        sp.next_track(device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Skips to previous track in user's queue
# Excepts:
#   device_id [STRING] (generated device id)
def previousTrack(request):
    response = False
    deviceID = request.POST['device_id']
    try:
        sp.previous_track(device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Sets shuffle status for a specific device
# Excepts:
#   device_id [STRING] (generated device id)
#   shuffle_status [STRING] ('enabled' || 'disabled')
def setShuffle(request):
    response = False
    if request.POST['shuffle_status'] != 'enabled' and request.POST['shuffle_status'] != 'disabled':
        return HttpResponse(response)
    deviceID = request.POST['device_id']
    shuffleState = request.POST['shuffle_status'] == 'enabled'
    try:
        sp.shuffle(state=shuffleState, device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)

