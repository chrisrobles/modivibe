# All views here will be dedicated to API calls
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from ..SpotifyApiObjs import sp, auth_manager
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
from django.template.loader import render_to_string
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

# Helper function to return a dictionary containing device info
# Expects:
#   device_id [STRING] (generated device id)
def getDeviceInfo(deviceID):
    response = False
    try:
        userDevices = sp.devices().get('devices')
        for device in userDevices:
            if device.get('id') == deviceID:
                response = device
                break
    except SpotifyException:
        response = False
    return response

# Sets Spotify's active device to Modivibe
# Expects:
#   device_id [STRING] (generated device id)
def transferPlayback(request):
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
#   status [STRING] ('play' || 'pause') DEFAULT: 'play'
#   context_uri [STRING] (uri for provided track/playlist/album/etc) DEFAULT: None
def setPlayback(request):
    response = False
    deviceID = request.POST['device_id']
    songStatus = request.POST.get('status', 'play')
    contextURI = request.POST.get('context_uri', None)
    offsetURI = request.POST.get('offset_uri', None)

    contextType = None
    if contextURI:
        contextType = contextURI.split(':')[1]

    try:
        if songStatus == 'play' and not offsetURI:
            sp.start_playback(device_id=deviceID, context_uri=contextURI)
            response = True
        elif songStatus == 'play' and offsetURI:
            # If we're playing from the artist page, set the context to the top artist songs.
            if contextType == 'artist':
                artistTopTracks = sp.artist_top_tracks(artist_id=contextURI)
                topTrackURIs = [offsetURI]
                # Add top tracks to the current context and skip over the offset
                for song in artistTopTracks['tracks']:
                    currentURI = 'spotify:track:'+song['id']
                    if currentURI == offsetURI:
                        continue
                    topTrackURIs.append('spotify:track:'+song['id'])
                sp.start_playback(device_id=deviceID, uris=topTrackURIs, offset={"uri": offsetURI})
            else:
                sp.start_playback(device_id=deviceID, context_uri=contextURI, offset={"uri": offsetURI})
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
    deviceID = request.POST['device_id']
    songVolume = int(request.POST['volume'])
    try:
        sp.volume(volume_percent=songVolume, device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)

# Searches user devices to find Modivibe and determine set volume
# Expects:
#   device_id [STRING] (generated device id)
def getVolume(request):
    deviceID = request.POST['device_id']
    device = getDeviceInfo(deviceID)
    if device:
        response = device.get('volume_percent')
    else:
        response = False
    return HttpResponse(response)

# Skips to next track in user's queue
# Excepts:
#   device_id [STRING] (generated device id)
def nextTrack(request):
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
    deviceID = request.POST['device_id']
    shuffleStatus = request.POST['shuffle_status']
    if shuffleStatus != 'enabled' and shuffleStatus != 'disabled':
        return HttpResponse(response)
    shuffleState = shuffleStatus == 'enabled'
    try:
        sp.shuffle(state=shuffleState, device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)

# Sets repeat status for a specific device (3 modes)
# Excepts:
#   device_id [STRING] (generated device id)
#   repeat_status [STRING] (0, 1, 2)
def setRepeat(request):
    deviceID = request.POST['device_id']
    repeatStatus = request.POST.get('repeat_status', None)
    repeatStates = {
        '0': 'off',
        '1': 'context',
        '2': 'track'
    }
    repeatState = repeatStates.get(repeatStatus, None)
    try:
        sp.repeat(state=repeatState, device_id=deviceID)
        response = repeatState
    except SpotifyException:
        response = False
    return HttpResponse(response)

# Helper while developing the progress bar
def helperButton(request):
    response = False
    deviceID = request.POST['device_id']
    try:
        sp.current_playback(device_id=deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)

# Display all of the current user's playlists
# my/playlists
def myPlaylists(request):
    # check a user is authenticated
    # also refreshes token if expired
    if not validUser():
        return redirect('splash')

    startAt = 0
    lim = 50 # 50 is max for api request

    plInfo = sp.current_user_playlists(limit=lim, offset=startAt)
    numPLs = plInfo['total']    # total number of playlists the user has

    info = []

    for p in plInfo['items']:
        info.append({
        'contentImg':  p['images'][0]['url'] if p['images'] else 'default',
        'contentName': p['name'],
        'contentId' :  p['id']
        })

        # if there are still more playlists to get
    while lim + startAt < numPLs:
        startAt += lim
        plInfo = sp.current_user_playlists(limit=lim, offset=startAt)

        for p in plInfo['items']:
            info.append({
                'contentImg': p['images'][0]['url'] if p['images'] else 'default',
                'contentName': p['name'],
                'contentId': p['id']
            })

    if isAjaxRequest(request):
        collection = render_to_string('webplayer/collectionItems.html', context={"info" : info, "type": "playlist", "ajax": True})
        return JsonResponse({'collection': collection}, status=200)
    else:
        return render(request, 'webplayer/collectionItems.html', context={"info" : info, "type": "playlist", "ajax": False})

def playlist(request, playlist_id):

    if not validUser():
        return redirect('splash')

    if isAjaxRequest(request):
        startAt = 0
        lim = 100
        pNo = 1

        slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
        numSongs = slInfo['total'] # total number of songs in a playlist

        info = []


        for s in slInfo['items']:
            info.append({
                "songNum":       pNo,
                "songName":     s['track']['name'],
                "songId":       s['track']['id'],
                "songURI":      s['track']['uri'],
                "songArtist":   s['track']['artists'][0]['name'],
                "artistId":     s['track']['artists'][0]['id'],
                "songLength":   s['track']['duration_ms']
            })

            pNo += 1

        while lim + startAt < numSongs:
            startAt += lim
            slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
            for s in slInfo['items']:
                info.append({
                    "songNum":      pNo,
                    "songName":     s['track']['name'],
                    "songId":       s['track']['id'],
                    "songURI":      s['track']['uri'],
                    "songArtist":   s['track']['artists'][0]['name'],
                    "artistId":     s['track']['artists'][0]['id'],
                    "songLength":   s['track']['duration_ms']
                })

                pNo += 1

        page = createSongList(info, 'playlist', 'spotify:playlist:'+playlist_id)

        return JsonResponse({'page': page}, status=200)

    return HttpResponse("<h1>{}</h1>".format(playlist_id)) # fix this

def mySavedAlbums(request):
    #check if user is authenticated

    if not validUser():
        return redirect('splash')

    startAt = 0
    lim = 50 #max that the api allows

    albumInfo = sp.current_user_saved_albums(limit=lim, offset=startAt)
    numAlbums = albumInfo['total'] #total # of albums the user has saved

    info = []

    for a in albumInfo['items']:
        info.append({
            'contentImg': a['album']['images'][0]['url'] if a['album']['images'] else 'default',
            'contentName': a['album']['name'],
            'contentId': a['album']['id'],
            'artist': a['album']['artists'][0]['name'],
            'artistId': a['album']['artists'][0]['id'],
            'albumDate': a['album']['release_date'][0:4]
        })

    while lim + startAt < numAlbums:
        startAt += lim
        albumInfo = sp.current_user_saved_albums(limit=lim, offset=startAt)

        for a in albumInfo['items']:
            info.append({
            'contentImg': a['album']['images'][0]['url'] if a['album']['images'] else 'default',
            'contentName': a['album']['name'],
            'contentId': a['album']['id'],
            'artist': a['album']['artists'][0]['name'],
            'artistId': a['album']['artists'][0]['id'],
            'albumDate': a['album']['release_date'][0:4]
        })
            

    if isAjaxRequest(request):
        collection = render_to_string('webplayer/collectionItems.html', context={"info": info, "type": "album", "ajax": True})
        return JsonResponse({'collection': collection}, status=200)
    else:
        return render(request, 'webplayer/collectionItems.html', context={"info": info, "type": "album", "ajax": False})

def myArtists(request):

    if not validUser():
        return redirect('splash')

    lim = 50
    artistInfo = sp.current_user_followed_artists(limit=lim)
    info = []

    for a in artistInfo['artists']['items']:
        info.append({
            'contentImg':  a['images'][0]['url'] if a['images'] else 'default',
            'contentName': a['name'],
            'contentId' :  a['id']
        })

    while artistInfo['artists']['next']:
        lastArtistReceived = artistInfo['artists']['cursors']['after']
        artistInfo = sp.current_user_followed_artists(limit=lim, after=lastArtistReceived)

        for a in artistInfo['artists']['items']:
            info.append({
                'contentImg':   a['images'][0]['url'] if a['images'] else 'default',
                'contentName':  a['name'],
                'contentId':    a['id']
            })

    if isAjaxRequest(request):
        collection = render_to_string('webplayer/collectionItems.html', context={"info": info, "type": "artist", "ajax": True})
        return JsonResponse({'collection': collection}, status=200)
    else:
        return render(request, 'webplayer/collectionItems.html', context={"info": info, "type": "artist", "ajax": False})

def myPodcasts(request):

    if not validUser():
        return redirect('splash')

    startAt = 0
    lim = 50

    podcastInfo = sp.current_user_saved_shows(limit=lim, offset=startAt)
    total = podcastInfo['total']
    info = []

    for p in podcastInfo['items']:
        info.append({
            'contentImg':   p['show']['images'][0]['url'] if p['show']['images'] else 'default',
            'contentName':  p['show']['name'],
            'contentId':    p['show']['id'],
            'publisher':    p['show']['publisher']
        })

    while lim + startAt < total:
        startAt += lim
        podcastInfo = sp.current_user_saved_shows(limit=lim, offset=startAt)

        for p in podcastInfo['items']:
            info.append({
                'contentImg': p['show']['images'][0]['url'] if p['show']['images'] else 'default',
                'contentName': p['show']['name'],
                'contentId': p['show']['id'],
                'publisher': p['show']['publisher']
            })

    if isAjaxRequest(request):
        collection = render_to_string('webplayer/collectionItems.html', context={"info": info, "type": "podcast", "ajax": True})
        return JsonResponse({'collection': collection}, status=200)
    else:
        return render(request, 'webplayer/collectionItems.html', context={"info": info, "type": "podcast", "ajax": False})

def artist(request, artist_id):
    if not validUser():
        return redirect('splash')

    # create header info, turn this into a function
    header = getArtistHeaderInfo(sp, artist_id)

    # artist page is just their picture and information by default, tabs will be used to show anything
    if isAjaxRequest(request):
        page = render_to_string('webplayer/artistPage.html',
                        context={"header": header, "ajax": True, "loadContent": False})
        return JsonResponse({"page": page}, status=200)
    else:
        return render(request, 'webplayer/artistPage.html',
                        context={"header": header, "ajax": False, "loadContent": False})

def artistTopSongs(request, artist_id):
    info = []
    top = sp.artist_top_tracks(artist_id)
    sn = 1
    for song in top['tracks']:
        info.append({
            'songNum': sn,
            'songName': song['name'],
            'songId': song['id'],
            'songLength': song['duration_ms'],
            'songAlbum': song['album']['name'],
            'songAlbumId': song['album']['id'],
            'songURI': song['uri'],
            'artistId': song['album']['artists'][0]['id'],
            'songArtist': song['album']['artists'][0]['name']
        })

        sn += 1

    content = createSongList(info, 'artist', 'spotify:artist:'+artist_id)

    if isAjaxRequest(request):
        return JsonResponse({"content": content}, status=200)
    else:
        # if not ajax, have to get header info and insert content string into template
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                        context={"header": header, "content": content, "contentType": "topSongs",
                                 "loadContent": True, "ajax": False})

def artistAlbums(request, artist_id):
    if not validUser():
        return redirect('splash')

    info = []
    lim = 50
    startAt = 0
    albums = sp.artist_albums(artist_id, album_type='album,single', limit=lim, offset=startAt)
    numAlbums = albums['total']

    for a in albums['items']:
        info.append({
            'contentImg': a['images'][0]['url'] if a['images'] else 'default',
            'contentName': a['name'],
            'contentId': a['id'],
            'artist': a['artists'][0]['name'],
            'artistId': a['artists'][0]['id'],
            'albumDate': a['release_date'][0:4]
        })

    while lim + startAt < numAlbums:
        startAt += lim
        albums = sp.artist_albums(artist_id, album_type='album,single', limit=lim, offset=startAt)
        
        for a in albums['items']:
            info.append({
            'contentImg': a['images'][0]['url'] if a['images'] else 'default',
            'contentName': a['name'],
            'contentId': a['id'],
            'artist': a['artists'][0]['name'],
            'artistId': a['artists'][0]['id'],
            'albumDate': a['release_date'][0:4]
        })

    content = render_to_string('webplayer/collectionItems.html',
                               context={"info": info, "type": "album", "ajax": True})

    # if ajax, just insert the collection of items into the page
    if isAjaxRequest(request):
        return JsonResponse({"content": content}, status=200)
    else:
        # if not ajax, have to get header info and insert content string into template
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                      context={"header": header, "content": content, "contentType": "albums",
                               "loadContent": True, "ajax": False})

def artistRelated(request, artist_id):
    if not validUser():
        return redirect('splash')

    # gets 20 related artists
    related = sp.artist_related_artists(artist_id)
    info = []

    for artist in related['artists']:
        info.append({
            'contentImg': artist['images'][0]['url'] if artist['images'] else 'default',
            'contentName': artist['name'],
            'contentId': artist['id']
        })

    content = render_to_string('webplayer/collectionItems.html', context={"info": info, "type": "artist", "ajax": True})

    if isAjaxRequest(request):
        return JsonResponse({"content": content}, status=200)
    else:
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                      context={"header": header, "content": content, "contentType": "related",
                               "loadContent": True, "ajax": False})


def settings(request):
    if not validUser():
        return redirect('splash')

    if isAjaxRequest(request):
        page = render_to_string('webplayer/settings.html', context={"ajax": True})
        return JsonResponse({"page": page}, status=200)
    else:
        return render(request, 'webplayer/settings.html', context={"ajax": False})
