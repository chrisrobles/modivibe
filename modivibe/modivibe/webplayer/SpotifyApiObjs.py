import spotipy
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from modivibe.settings import env

# DON'T CHANGE ANY OF THE VARIABLES IN HERE pls

# May need to write our own cache_handler, cache handled by spotipy defaults right now

scope = [
    'ugc-image-upload',
    'user-read-recently-played',
    'user-top-read',
    'user-read-playback-position',
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'app-remote-control',
    'streaming',
    'playlist-modify-public',
    'playlist-modify-private',
    'playlist-read-private',
    'playlist-read-collaborative',
    'user-follow-modify',
    'user-follow-read',
    'user-library-modify',
    'user-library-read',
    'user-read-email',
    'user-read-private'
]

auth_manager = SpotifyOAuth(client_id=env('CLIENT_ID'),
                            client_secret=env('CLIENT_SECRET'),
                            redirect_uri=env('REDIRECT_URI'),
                            scope=' '.join(scope))

sp = spotipy.Spotify(auth_manager=auth_manager)
