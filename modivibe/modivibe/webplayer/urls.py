from django.urls import path
from . import views

urlpatterns = [
    # WEBSITE PAGES
    # path('admin/', admin.site.urls),
    path('', views.splash, name='splash'),
    path('webplayer', views.home, name='webplayer'),
    path('webplayer/settings', views.settings, name='webplayer/settings'),

    # SPOTIPY API
    path('redirectToHome', views.redirectToHome, name='redirectToHome'),
    path('transferPlayback', views.transferPlayback, name='transferPlayback'),
    path('setPlayback', views.setPlayback, name='setPlayback'),
    path('setVolume', views.setVolume, name='setVolume'),
    path('nextTrack', views.nextTrack, name='nextTrack'),
    path('previousTrack', views.previousTrack, name='previousTrack'),

    # user collections and music collections (albums, artists, playlists, podcasts)
    # url should follow:    my/{collection_type}s
    #                       {collection_type}/<str:type_id>
    path('my/playlists', views.myplaylists, name='myplaylists'),
    path('playlist/<str:playlist_id>', views.playlist, name='playlist')
]