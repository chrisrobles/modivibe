# All views here will be dedicated to API calls
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ..SpotifyApiObjs import sp, auth_manager
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
import pprint
from webplayer.views.create_html import *

def validUser():
    try:
        auth_manager.validate_token(auth_manager.cache_handler.get_cached_token())
    except:
        print('Access denied.')
        return False
    return True

def isAjaxRequest(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


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

# Display all of the current user's playlists
# my/playlists
def myplaylists(request):
    # check a user is authenticated
    # also refreshes token if expired
    if not validUser():
        return redirect('splash')

    if isAjaxRequest(request):
        startAt = 0
        lim = 50 # 50 is max for api request

        plInfo = sp.current_user_playlists(limit=lim, offset=startAt)
        numPLs = plInfo['total']    # total number of playlists the user has

        info = []

        for p in plInfo['items']:
            info.append({
            'contentImg':  p['images'][0]['url'] if p['images'] else 'default',
            'contentName': p['name'],
            'contentId' :  p['id'],
            'contentDesc': p['description']
            })

        # if there are still more playlists to get
        while lim + startAt < numPLs:
            startAt += lim
            plInfo = sp.current_user_playlists(limit=lim, offset=startAt)

            for p in plInfo['items']:
                info.append({
                    'contentImg': p['images'][0]['url'] if p['images'] else 'default',
                    'contentName': p['name'],
                    'contentId': p['id'],
                    'contentDesc': p['description']
                })

        playlists = createCollectionItems(info, 'playlist')

        return JsonResponse({'playlists': playlists}, status=200)

    return HttpResponse("no") # need to find a way to trigger ajax if we type the url

def playlist(request, playlist_id):

    if not validUser():
        return redirect('splash')

    if isAjaxRequest(request):
        startAt = 0
        lim = 100
        pNo = 1

        slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
        numSongs = slInfo['total'] # total number of songs in a playlist

        num_artist_songname_dur = []


        for s in slInfo['items']:
            num_artist_songname_dur.append({
                "songNo": pNo,
                "artist": s['track']['artists'][0]['name'],
                "songName":   s['track']['name'],
                "length": s['track']['duration_ms']
            })

            pNo += 1

        while lim + startAt < numSongs:
            startAt += lim
            slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
            for s in slInfo['items']:
                num_artist_songname_dur.append({
                    "songNo": pNo,
                    "artist": s['track']['artists'][0]['name'],
                    "songName": s['track']['name'],
                    "length": s['track']['duration_ms']
                })

                pNo += 1

        return JsonResponse({'songlist': num_artist_songname_dur}, status=200)

    return HttpResponse("<h1>{}</h1>".format(playlist_id)) # fix this