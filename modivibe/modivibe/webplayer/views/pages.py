# All views here will be dedicated to rendering page content
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from ..SpotifyApiObjs import sp, auth_manager
from spotipy.oauth2 import SpotifyOauthError
from .spotipy_api import validUser, isAjaxRequest, getUserAccessCode, getContextURIInfo
from .create_html import *
from json import dumps
from django.views.decorators.csrf import csrf_exempt


# Login flow: splash, click loginurl -> redirectToHome -> splash or home
def splash(request):
    context = {
        'title': 'Splash',
        'loginurl': auth_manager.get_authorize_url()
    }
    return render(request, 'webplayer/splash.html', context)

@csrf_exempt
def home(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    recentlyPlayedList = sp.current_user_recently_played(limit=32)
    import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(recentlyPlayedList)
    RecentlyPlayed = []
    for a in recentlyPlayedList['items']:
        RecentlyPlayed.append({
            'contentImg': a['track']['album']['images'][1]['url'] if a['track']['album']['images'] else 'default',
            'contentName': a['track']['album']['name'],
            'contentId': a['track']['album']['id'],
            'artist': a['track']['album']['artists'][0]['name'],
            'artistId': a['track']['album']['artists'][0]['id'],
            'albumDate': a['track']['album']['release_date'][0:4],
        })

    collectionContext = {
        'type': 'album',
        'ajax': True,
        'info': RecentlyPlayed,
        'skipHeader': True
    }

    RecentlyPlayedContent = render_to_string("webplayer/collectionItems.html", context=collectionContext)

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'RecentlyPlayed': RecentlyPlayedContent
    }

    if context['ajax'] is True:
        page = render_to_string('webplayer/home.html', context=context)
        return JsonResponse({"collection": page, 'status': 200})
    else:
        return render(request, 'webplayer/home.html', context=context)

@csrf_exempt
def recommendations(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    referenceURI = request.POST.get('context_uri', None)
    referenceInfo = getContextURIInfo(referenceURI) if referenceURI else None
    referenceString = dumps(referenceInfo)
    print('Loading:', referenceString)

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'referenceInfo': referenceInfo,
        'referenceString': referenceString
    }

    if context['ajax'] is True:
        page = render_to_string('webplayer/recommendations.html', context=context)
        return JsonResponse({"page": page, 'status': 200})
    else:
        return render(request, 'webplayer/recommendations.html', context=context)

@csrf_exempt
def settings(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request)
    }

    if context['ajax']:
        page = render_to_string('webplayer/settings.html', context=context)
        return JsonResponse({"page": page, 'status': 200})
    else:
        return render(request, 'webplayer/settings.html', context=context)


# Display all of the current user's playlists
# my/playlists
@csrf_exempt
def myPlaylists(request):
    # check a user is authenticated
    # also refreshes token if expired
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    startAt = 0
    lim = 50  # 50 is max for api request

    plInfo = sp.current_user_playlists(limit=lim, offset=startAt)
    numPLs = plInfo['total']  # total number of playlists the user has

    # for showing the number of liked songs on the button
    likedSongsInfo = sp.current_user_saved_tracks(limit=lim, offset=startAt)
    numOfLikedSongs = likedSongsInfo['total']  # total number of liked songs

    info = []

    for p in plInfo['items']:
        info.append({
            'contentImg': p['images'][0]['url'] if p['images'] else None,
            'contentName': p['name'],
            'contentId': p['id']
        })

        # if there are still more playlists to get
    while lim + startAt < numPLs:
        startAt += lim
        plInfo = sp.current_user_playlists(limit=lim, offset=startAt)

        for p in plInfo['items']:
            info.append({
                'contentImg': p['images'][0]['url'] if p['images'] else None,
                'contentName': p['name'],
                'contentId': p['id']
            })

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'info': info,
        'type': 'playlist',
        'numOfLikedSongs': numOfLikedSongs,
    }

    if context['ajax'] is True:
        collection = render_to_string('webplayer/collectionItems.html', context=context)
        return JsonResponse({'collection': collection, 'status': 200})
    else:
        return render(request, 'webplayer/collectionItems.html', context=context)

@csrf_exempt
def playlist(request, playlist_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    if isAjaxRequest(request):
        startAt = 0
        lim = 100
        pNo = 1

        slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
        numSongs = slInfo['total']  # total number of songs in a playlist

        info = []

        for s in slInfo['items']:
            info.append({
                "songNum": pNo,
                "songName": s['track']['name'],
                "songId": s['track']['id'],
                "songURI": s['track']['uri'],
                "songArtist": s['track']['artists'][0]['name'] if s['track'].get('artists') else "",
                "artistId": s['track']['artists'][0]['id'] if s['track'].get('artists') else "",
                "songLength": s['track']['duration_ms']
            })

            pNo += 1

        while lim + startAt < numSongs:
            startAt += lim
            slInfo = sp.playlist_items(playlist_id=playlist_id, limit=lim, offset=startAt)
            for s in slInfo['items']:
                info.append({
                    "songNum": pNo,
                    "songName": s['track']['name'],
                    "songId": s['track']['id'],
                    "songURI": s['track']['uri'],
                    "songArtist": s['track']['artists'][0]['name'] if s['track'].get('artists') else "",
                    "artistId": s['track']['artists'][0]['id'] if s['track'].get('artists') else "",
                    "songLength": s['track']['duration_ms']
                })

                pNo += 1

        # TODO: Make the songList an actual HTML page then utilize context & render_to_string
        page = createSongList(info, 'playlist', 'spotify:playlist:' + playlist_id)

        return JsonResponse({'page': page, 'status': 200})

    return redirect('webplayer')  # fix this <------- need html page

@csrf_exempt
def album(request, album_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    if isAjaxRequest(request):
        startAt = 0
        lim = 50
        pNo = 1

        slInfo = sp.album_tracks(album_id=album_id, limit=lim, offset=startAt)
        num_songs = slInfo['total']  # total number of songs in an album

        info = []

        for s in slInfo['items']:
            info.append({
                "songNum": pNo,
                "songName": s['name'],
                "songId": s['id'],
                "songURI": s['uri'],
                "songArtist": s['artists'][0]['name'] if s.get('artists') else "",
                "artistId": s['artists'][0]['id'] if s.get('artists') else "",
                "songLength": s['duration_ms']
            })

            pNo += 1

        while lim + startAt < num_songs:
            startAt += lim
            slInfo = sp.album_tracks(album_id=album_id, limit=lim, offset=startAt)
            for s in slInfo['items']:
                info.append({
                    "songNum": pNo,
                    "songName": s['name'],
                    "songId": s['id'],
                    "songURI": s['uri'],
                    "songArtist": s['artists'][0]['name'] if s.get('artists') else "",
                    "artistId": s['artists'][0]['id'] if s.get('artists') else "",
                    "songLength": s['duration_ms']
                })

                pNo += 1

        # TODO: Make the songList an actual HTML page then utilize context & render_to_string
        page = createSongList(info, 'album', 'spotify:album:' + album_id)

        return JsonResponse({'page': page, 'status': 200})

    return redirect('webplayer')  # fix this <------- need html page

def mySavedAlbums(request):
    # check if user is authenticated
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    startAt = 0
    lim = 50  # max that the api allows

    albumInfo = sp.current_user_saved_albums(limit=lim, offset=startAt)
    numAlbums = albumInfo['total']  # total # of albums the user has saved

    info = []

    for a in albumInfo['items']:
        info.append({
            'contentImg': a['album']['images'][0]['url'] if a['album']['images'] else None,
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
                'contentImg': a['album']['images'][0]['url'] if a['album']['images'] else None,
                'contentName': a['album']['name'],
                'contentId': a['album']['id'],
                'artist': a['album']['artists'][0]['name'],
                'artistId': a['album']['artists'][0]['id'],
                'albumDate': a['album']['release_date'][0:4]
            })

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'info': info,
        'type': 'album'
    }

    if context['ajax'] is True:
        collection = render_to_string('webplayer/collectionItems.html', context=context)
        return JsonResponse({'collection': collection, 'status': 200})
    else:
        return render(request, 'webplayer/collectionItems.html', context=context)

@csrf_exempt
def myArtists(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    lim = 50
    artistInfo = sp.current_user_followed_artists(limit=lim)
    info = []

    for a in artistInfo['artists']['items']:
        info.append({
            'contentImg': a['images'][0]['url'] if a['images'] else None,
            'contentName': a['name'],
            'contentId': a['id']
        })

    while artistInfo['artists']['next']:
        lastArtistReceived = artistInfo['artists']['cursors']['after']
        artistInfo = sp.current_user_followed_artists(limit=lim, after=lastArtistReceived)

        for a in artistInfo['artists']['items']:
            info.append({
                'contentImg': a['images'][0]['url'] if a['images'] else None,
                'contentName': a['name'],
                'contentId': a['id']
            })

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'info': info,
        'type': 'artist'
    }

    if context['ajax'] is True:
        collection = render_to_string('webplayer/collectionItems.html', context=context)
        return JsonResponse({'collection': collection, 'status': 200})
    else:
        return render(request, 'webplayer/collectionItems.html', context=context)

@csrf_exempt
def myPodcasts(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    startAt = 0
    lim = 50

    podcastInfo = sp.current_user_saved_shows(limit=lim, offset=startAt)
    total = podcastInfo['total']
    info = []

    for p in podcastInfo['items']:
        info.append({
            'contentImg': p['show']['images'][0]['url'] if p['show']['images'] else None,
            'contentName': p['show']['name'],
            'contentId': p['show']['id'],
            'publisher': p['show']['publisher']
        })

    while lim + startAt < total:
        startAt += lim
        podcastInfo = sp.current_user_saved_shows(limit=lim, offset=startAt)

        for p in podcastInfo['items']:
            info.append({
                'contentImg': p['show']['images'][0]['url'] if p['show']['images'] else None,
                'contentName': p['show']['name'],
                'contentId': p['show']['id'],
                'publisher': p['show']['publisher']
            })

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'info': info,
        'type': 'podcast'
    }

    if context['ajax'] is True:
        collection = render_to_string('webplayer/collectionItems.html', context=context)
        return JsonResponse({'collection': collection, 'status': 200})
    else:
        return render(request, 'webplayer/collectionItems.html', context=context)

@csrf_exempt
def myLikedSongs(request):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    startAt = 0
    # limit of 50 or the API call will fail
    lim = 50
    songNum = 1

    likedSongsInfo = sp.current_user_saved_tracks(limit=lim, offset=startAt)
    numOfSongs = likedSongsInfo['total']  # total number of liked songs

    likedSongsTrimmedInfo = []

    for s in likedSongsInfo['items']:
        likedSongsTrimmedInfo.append({
            "songNum": songNum,
            "songName": s['track']['name'],
            "songId": s['track']['id'],
            "songURI": s['track']['uri'],
            "songArtist": s['track']['artists'][0]['name'] if s['track'].get('artists') else "",
            "artistId": s['track']['artists'][0]['id'] if s['track'].get('artists') else "",
            "songLength": s['track']['duration_ms'],
            'songAlbumURI': s['track']['album']['uri'],
        })

        songNum += 1

    while lim + startAt < numOfSongs:
        startAt += lim

        likedSongsInfo = sp.current_user_saved_tracks(limit=lim, offset=startAt)
        for s in likedSongsInfo['items']:
            likedSongsTrimmedInfo.append({
                "songNum": songNum,
                "songName": s['track']['name'],
                "songId": s['track']['id'],
                "songURI": s['track']['uri'],
                "songArtist": s['track']['artists'][0]['name'] if s['track'].get('artists') else "",
                "artistId": s['track']['artists'][0]['id'] if s['track'].get('artists') else "",
                "songLength": s['track']['duration_ms'],
                'songAlbumURI': s['track']['album']['uri'],
            })

            songNum += 1

    # TODO: Make the songList an actual HTML page then utilize context & render_to_string
    uriPlaceholder = "URI:PLACE:HOLDER"
    page = createSongList(likedSongsTrimmedInfo, 'liked songs', uriPlaceholder)

    # fix this replace with the correct URI string for the liked strings page to allow the PLAY ALL button to work
    #   note: not really sure if that is possible with what we're given by spotipy/spotify
    page = page.replace(uriPlaceholder, 'fix me luls', 1)

    # needed for each song to be playable from the list
    for song in likedSongsTrimmedInfo:
        page = page.replace(uriPlaceholder, song['songAlbumURI'], 2)

    return JsonResponse({'page': page, 'status': 200})

@csrf_exempt
def artist(request, artist_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    # create header info, turn this into a function
    header = getArtistHeaderInfo(sp, artist_id)

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        'header': header,
        'loadContent': False
    }

    # artist page is just their picture and information by default, tabs will be used to show anything
    if context['ajax'] is True:
        page = render_to_string('webplayer/artistPage.html', context=context)
        return JsonResponse({"page": page, 'status': 200})
    else:
        return render(request, 'webplayer/artistPage.html', context=context)

@csrf_exempt
def artistTopSongs(request, artist_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

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

    # TODO: Once this is an HTML page, use the context variable like other pages
    content = createSongList(info, 'artist', 'spotify:artist:' + artist_id)

    if isAjaxRequest(request):
        print('***** views.artistTopSongs() fired , is an ajax request *****')

        return JsonResponse({"content": content, 'status': 200})
    else:
        print('***** views.artistTopSongs() fired , is NOT an ajax request *****')

        # if not ajax, have to get header info and insert content string into template
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                      context={"header": header, "content": content, "contentType": "topSongs",
                               "loadContent": True, "ajax": False, "userAccessCode": userAccessCode})

@csrf_exempt
def artistAlbums(request, artist_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    info = []
    lim = 50
    startAt = 0
    albums = sp.artist_albums(artist_id, album_type='album,single', limit=lim, offset=startAt)
    numAlbums = albums['total']

    for a in albums['items']:
        info.append({
            'contentImg': a['images'][0]['url'] if a['images'] else None,
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
                'contentImg': a['images'][0]['url'] if a['images'] else None,
                'contentName': a['name'],
                'contentId': a['id'],
                'artist': a['artists'][0]['name'],
                'artistId': a['artists'][0]['id'],
                'albumDate': a['release_date'][0:4]
            })

    # TODO: Change the way we handle this to use context variable like other pages (if possible)
    content = render_to_string('webplayer/collectionItems.html',
                               context={"info": info, "type": "album", "ajax": True, "userAccessCode": userAccessCode})

    # if ajax, just insert the collection of items into the page
    if isAjaxRequest(request):
        return JsonResponse({"content": content, 'status': 200})
    else:
        # if not ajax, have to get header info and insert content string into template
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                      context={"header": header, "content": content, "contentType": "albums",
                               "loadContent": True, "ajax": False, "userAccessCode": userAccessCode})

@csrf_exempt
def artistRelated(request, artist_id):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    # gets 20 related artists
    related = sp.artist_related_artists(artist_id)
    info = []

    for artist in related['artists']:
        info.append({
            'contentImg': artist['images'][0]['url'] if artist['images'] else None,
            'contentName': artist['name'],
            'contentId': artist['id']
        })

    # TODO: Change the way we handle this to use context variable like other pages (if possible)
    content = render_to_string('webplayer/collectionItems.html',
                               context={"info": info, "type": "artist", "ajax": True, "userAccessCode": userAccessCode})

    if isAjaxRequest(request):
        return JsonResponse({"content": content, 'status': 200})
    else:
        header = getArtistHeaderInfo(sp, artist_id)
        return render(request, 'webplayer/artistPage.html',
                      context={"header": header, "content": content, "contentType": "related",
                               "loadContent": True, "ajax": False, "userAccessCode": userAccessCode})


# Never return search_value back to ajax directly!!! (users would be able to insert html)
# Render cleans input
@csrf_exempt
def search(request, search_value):
    if not validUser(request):
        return JsonResponse({'status': 401}) if isAjaxRequest(request) else redirect('splash')

    userAccessCode = getUserAccessCode()
    if not userAccessCode:
        return redirect('splash')

    sr = sp.search(search_value, type="track,album,artist,playlist", limit=8)

    # tracks
    tracks = []
    sn = 1
    for tr in sr['tracks']['items']:
        tracks.append({
            'songNum': sn,
            'songName': tr['name'],
            'songId': tr['id'],
            'songLength': tr['duration_ms'],
            'songAlbum': tr['album']['name'],
            'songAlbumId': tr['album']['id'],
            'songURI': tr['uri'],
            'artistId': tr['album']['artists'][0]['id'],
            'songArtist': tr['album']['artists'][0]['name'],
            'songAlbumURI': tr['album']['uri']
        })

        sn += 1

    uriPlaceholder = "URI:PLACE:HOLDER"
    trackRes = createSongList(tracks, "playlist", uriPlaceholder)

    # replace individual track uris
    # replace play request uri first
    trackRes = trackRes.replace(uriPlaceholder, 'button machine broke pls delete in js', 1)

    for track in tracks:
        trackRes = trackRes.replace(uriPlaceholder, track['songAlbumURI'], 2)

    # artists
    artists = []
    for ar in sr['artists']['items']:
        artists.append({
            'contentImg': ar['images'][0]['url'] if ar['images'] else None,
            'contentName': ar['name'],
            'contentId': ar['id']
        })

    artistRes = render_to_string('webplayer/collectionItems.html',
                                 context={"info": artists, "type": "artist", "ajax": True})

    # albums
    albums = []
    for al in sr['albums']['items']:
        albums.append({
            'contentImg': al['images'][0]['url'] if al['images'] else None,
            'contentName': al['name'],
            'contentId': al['id'],
            'artist': al['artists'][0]['name'],
            'artistId': al['artists'][0]['id'],
            'albumDate': al['release_date'][0:4]
        })

    albumRes = render_to_string('webplayer/collectionItems.html',
                                context={"info": albums, "type": "album", "ajax": True})

    # playlists
    playlists = []
    for pl in sr['playlists']['items']:
        playlists.append({
            'contentImg': pl['images'][0]['url'] if pl['images'] else None,
            'contentName': pl['name'],
            'contentId': pl['id']
        })

    playlistRes = render_to_string('webplayer/collectionItems.html',
                                   context={"info": playlists, "type": "playlist", "ajax": True})

    context = {
        'userAccessCode': userAccessCode,
        'ajax': isAjaxRequest(request),
        "tracks": trackRes,
        "artists": artistRes,
        "albums": albumRes,
        "playlists": playlistRes,
        "searchValue": search_value
    }

    if isAjaxRequest(request):
        return JsonResponse(
            {"searchResults": render_to_string('webplayer/search.html', context=context), 'status': 200})
    else:
        return render(
            request, 'webplayer/search.html', context=context)


def view404error(request, exception):
    return render(request, 'webplayer/404.html')


def view500error(request):
    return render(request, 'webplayer/500.html')


# def view404test(request):
#     return render(request, 'webplayer/404.html')
#
#
# def view500test(request):
#     return render(request, 'webplayer/500.html')
