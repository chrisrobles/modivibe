import spotipy
from spotipy.oauth2 import SpotifyOAuth, CacheHandler
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

class ModivibeCache(CacheHandler):
    def __init__(self):
        self.session = None

    def set_session(self, session):
        self.session = session

    def get_session(self):
        return self.session

    def get_cached_token(self):
        token = None
        if self.session['modivibe_access']:
            token = self.session['modivibe_access']
        return token

    def save_token_to_cache(self, token_info):
        self.session.clear()

        if token_info:
            self.session['modivibe_access'] = token_info

    def delete_session(self):
        self.session.clear()

cache_handler = ModivibeCache()

auth_manager = SpotifyOAuth(client_id=env('CLIENT_ID'),
                            client_secret=env('CLIENT_SECRET'),
                            redirect_uri=env('REDIRECT_URI'),
                            cache_handler= cache_handler,
                            scope=' '.join(scope))

sp = spotipy.Spotify(auth_manager=auth_manager)
