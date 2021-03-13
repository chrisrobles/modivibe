import spotipy
from spotipy.oauth2 import SpotifyOAuth
from modivibe.modivibe.settings import env

# DON'T CHANGE ANY OF THE VARIABLES IN HERE pls

auth_manager = SpotifyOAuth(client_id=env('CLIENT_ID'),
                            client_secret=env('CLIENT_SECRET'),
                            redirect_uri=env('REDIRECT_URI'),
                            scope='user-library-read')

sp = spotipy.Spotify(auth_manager=auth_manager)