from django.urls import path
from . import views

urlpatterns = [
    # WEBSITE PAGES
    # path('admin/', admin.site.urls),
    path('', views.splash, name='splash'),
    path('webplayer', views.home, name='webplayer'),
    path('settings', views.settings, name='settings'),

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
    path('toggleFollow', views.toggleFollow, name='toggleFollow'),
    path('toggleLike', views.toggleLike, name='toggleLike'),
    path('isFollowing', views.isFollowing, name='isFollowing'),
    path('isLiked', views.isLiked, name='isLiked'),
    path('progressBarSldrMoved', views.progressBarSldrMoved, name='progressBarSldrMoved'),

    # user collections and music collections (albums, artists, playlists, podcasts)
    # url should follow:    my/{collection_type}s
    path('my/playlists', views.myPlaylists, name='myPlaylists'),
    path('my/albums', views.mySavedAlbums, name='myAlbums'),
    path('my/artists', views.myArtists, name='myArtists'),
    path('my/podcasts', views.myPodcasts, name='myPodcasts'),
    path('my/likedSongs', views.myLikedSongs, name='likedSongs'),

    # displays an item's page
    # url should follow:    {collection_type}/<str:type_id>
    path('playlist/<str:playlist_id>', views.playlist, name='playlist'),
    path('artist/<str:artist_id>', views.artist, name='artist'),
    path('artist/<str:artist_id>/topSongs', views.artistTopSongs, name='artistTopSongs'),
    path('artist/<str:artist_id>/albums', views.artistAlbums, name='artistAlbums'),
    path('artist/<str:artist_id>/related', views.artistRelated, name='artistRelated'),

    # search bar
    path('search/<str:search_value>', views.search, name='search'),

    # recommendations
    path('recommendations', views.recommendations, name='recommendations'),
    path('getRecommendations', views.getRecommendations, name='getRecommendations'),

    # logout
    path('logout', views.logout, name='logout'),
    
    # error pages (for testing purposes)
    #path('404', views.view404test, name='404Handler'),
    #path('500', views.view500test, name='500Handler'),
]
