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
    path('getVolume', views.getVolume, name='getVolume'),
    path('nextTrack', views.nextTrack, name='nextTrack'),
    path('previousTrack', views.previousTrack, name='previousTrack'),
    path('setShuffle', views.setShuffle, name='setShuffle'),
    path('setRepeat', views.setRepeat, name='setRepeat'),
    path('helperButton', views.helperButton, name='helperButton'),
    path('recentlyPlayedList', views.getRecentPlayed, name='getRecentPlayed'),

    # user collections and music collections (albums, artists, playlists, podcasts)
    # url should follow:    my/{collection_type}s
    path('my/playlists', views.myPlaylists, name='myPlaylists'),
    path('my/albums', views.mySavedAlbums, name='myAlbums'),
    path('my/artists', views.myArtists, name='myArtists'),
    path('my/podcasts', views.myPodcasts, name='myPodcasts'),

    # displays an item's page
    # url should follow:    {collection_type}/<str:type_id>
    path('playlist/<str:playlist_id>', views.playlist, name='playlist'),

]
