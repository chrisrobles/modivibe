# All views here will be dedicated to API calls
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from ..SpotifyApiObjs import sp, auth_manager, cache_handler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
from .create_html import *
from random import choice, sample
import json
import pprint


def validUser(request):
    cache_handler.set_session(request.session) # leave in or take out? better to update or not?

    try:
        auth_manager.validate_token(auth_manager.cache_handler.get_cached_token())
    except:
        print('Access denied.')
        return False
    return True


def getUserAccessCode():
    try:
        code = auth_manager.get_access_token().get('access_token')
        return code
    except:
        return None


def isAjaxRequest(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def getContextURIInfo(referenceURI):
    referenceData = None
    referenceType = referenceURI.split(':')[1]
    if referenceType == 'artist':
        artistInfo = sp.artist(referenceURI)
        referenceData = {
            'type': referenceType,
            'name': artistInfo['name'],
            'image': artistInfo['images'][0]['url'] if artistInfo['images'] else 'default',
            'uri': artistInfo['uri'],
            'genres': artistInfo['genres'][:7],
        }
    elif referenceType == 'album':
        albumInfo = sp.album(referenceURI)
        artistURI = albumInfo['artists'][0]['uri']
        artistInfo = sp.artist(artistURI)
        if len(albumInfo['genres']) > 0:
            genres = albumInfo['genres']
        else:
            genres = artistInfo['genres']
        referenceData = {
            'type': referenceType,
            'name': albumInfo['name'],
            'image': albumInfo['images'][0]['url'] if albumInfo['images'] else 'default',
            'uri': albumInfo['uri'],
            'genres': genres[:7],
            'artistURI': albumInfo['artists'][0]['uri'],
            'artistName': artistInfo['name']
        }
    elif referenceType == 'playlist':
        playlistInfo = sp.playlist(referenceURI)
        tracks = []
        if len(playlistInfo['tracks']['items']) > 15:
            randomTracks = sample(playlistInfo['tracks']['items'], 15)
        else:
            randomTracks = playlistInfo['tracks']['items']
        for track in randomTracks:
            trackURI = track['track']['uri']
            if trackURI.split(':')[1] == 'local':
                continue
            tracks.append(trackURI)
        referenceData = {
            'type': referenceType,
            'name': playlistInfo['name'],
            'image': playlistInfo['images'][0]['url'] if playlistInfo['images'] else 'default',
            'uri': playlistInfo['uri'],
            'tracks': tracks
        }
    elif referenceType == 'track':
        trackInfo = sp.track(referenceURI)
        albumInfo = sp.album_tracks(trackInfo['album']['uri'])
        tracks = [referenceURI]
        if len(albumInfo['items']) > 3:
            randomTracks = sample(albumInfo['items'], 3)
        else:
            randomTracks = albumInfo['items']
        for track in randomTracks:
            trackURI = track['uri']
            tracks.append(trackURI)

        trackFeatures = sp.audio_features(referenceURI)
        features = {
            'acousticness': trackFeatures[0]['acousticness'],
            'danceability': trackFeatures[0]['danceability'],
            'energy': trackFeatures[0]['energy'],
            'instrumentalness': trackFeatures[0]['instrumentalness'],
            'key': trackFeatures[0]['key'],
            'liveness': trackFeatures[0]['liveness'],
            'loudness': trackFeatures[0]['loudness'],
            'speechiness': trackFeatures[0]['speechiness'],
            'tempo': trackFeatures[0]['tempo'],
            'valence': trackFeatures[0]['valence']
        }

        referenceData = {
            'type': referenceType,
            'name': trackInfo['name'],
            'image': trackInfo['album']['images'][0]['url'] if trackInfo['album']['images'] else 'default',
            'uri': trackInfo['uri'],
            'artistURI': trackInfo['artists'][0]['uri'],
            'artistName': trackInfo['artists'][0]['name'],
            'tracks': tracks,
            'trackFeatures': features
        }
    return referenceData

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
        cache_handler.set_session(request.session)
        auth_manager.get_access_token(request.GET['code'], check_cache=False, as_dict=False)
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


# Sets the following status for a specific artist
# Excepts:
#   artist [STRING] (the artist uri)
#   follow [STRING] ('true' || 'false')
def toggleFollow(request):
    response = False
    artistURI = request.POST.get('artist', None)
    follow = request.POST.get('follow', None)
    artistURI = artistURI.split(':')[2]
    artistList = [artistURI]

    try:
        if follow is None:
            response = False
        elif follow == 'true':
            sp.user_follow_artists(ids=artistList)
            response = True
        elif follow == 'false':
            sp.user_unfollow_artists(ids=artistList)
            response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Sets the like status for a specific track
# Excepts:
#   track [STRING] (the track uri)
#   like [STRING] ('true' || 'false')
def toggleLike(request):
    response = False
    trackURI = request.POST.get('track', None)
    like = request.POST.get('like', None)
    trackURI = trackURI.split(':')[2]
    trackList = [trackURI]

    try:
        if like is None:
            response = False
        elif like == 'true':
            sp.current_user_saved_tracks_add(tracks=trackList)
            response = True
        elif like == 'false':
            sp.current_user_saved_tracks_delete(tracks=trackList)
            response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Checks if the user is following a specific artist.
# If so, return the artist URI and follow status for asynchronous calls
# Excepts:
#   artist [STRING] (the artist uri)
def isFollowing(request):
    artistURI = request.POST.get('artist', None)
    artistList = [artistURI]
    try:
        boolFollowList = sp.current_user_following_artists(ids=artistList)
        response = JsonResponse({"artist": artistURI, "following": boolFollowList[0]}, status=200)
    except SpotifyException:
        response = False
    return HttpResponse(response)


# Checks if the user likes a specific track
# If so, return the track URI and like status for asynchronous calls
# Excepts:
#   track [STRING] (the track uri)
def isLiked(request):
    trackURI = request.POST.get('track', None)
    trackList = [trackURI]
    try:
        boolFollowList = sp.current_user_saved_tracks_contains(tracks=trackList)
        response = JsonResponse({"track": trackURI, "liked": boolFollowList[0]}, status=200)
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


def getRecommendations(request):
    reference = request.POST.get('reference', None)
    if not reference:
        return HttpResponse(False)
    reference = json.loads(reference)

    genres, tracks, artists = [], [], []
    if reference['type'] == 'artist':
        artists = [reference['uri']]
        genres = reference['genres'][:4]
        # Total Seeds: (1) artist + (1-4) genres
    elif reference['type'] == 'album':
        artists = [reference['artistURI']]
        genres = reference['genres'][:3]
        albumTracks = sp.album_tracks(reference['uri'])
        randomTrack = choice(albumTracks['items'])
        tracks.append(randomTrack['uri'])
        # Total Seeds: (1) artist + (1-3) genres + (1) track from album
    elif reference['type'] == 'playlist':
        tracks = reference['tracks'][:5]
        # Total Seeds: (5) tracks from playlist
    elif reference['type'] == 'track':
        artists = [reference['artistURI']]
        tracks = reference['tracks'][:4]
        # Total Seeds: (1) artists + (1-4) track & tracks from album
    else:
        return HttpResponse(False)
    print('Seeds:', genres, tracks, artists)

    features = request.POST.get('features', None)
    if not features:
        return HttpResponse(False)
    features = json.loads(features)

    try:
        generatedRecommendations = sp.recommendations(
            seed_genres=genres,
            seed_tracks=tracks,
            seed_artists=artists,
            limit=20,
            target_acousticness=features.get('acousticness', None),
            target_danceability=features.get('danceability', None),
            target_energy=features.get('energy', None),
            target_instrumentalness=features.get('instrumentalness', None),
            target_key=features.get('key', None),
            target_liveness=features.get('liveness', None),
            target_loudness=features.get('loudness', None),
            target_speechiness=features.get('speechiness', None),
            target_tempo=features.get('tempo', None),
            target_valence=features.get('valence', None)
        )
        print('Recommendations:', generatedRecommendations)
        return JsonResponse(generatedRecommendations, status=200)
    except SpotifyException:
        return HttpResponse(False)


def progressBarSldrMoved(request):
    deviceID = request.POST['device_id']
    songPositionMs = int(request.POST['position_ms'])

    try:
        sp.seek_track(songPositionMs, deviceID)
        response = True
    except SpotifyException:
        response = False
    return HttpResponse(response)
