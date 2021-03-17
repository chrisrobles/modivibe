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
    path('setPlayback', views.setPlayback, name='setPlayback'),
    path('setVolume', views.setVolume, name='setVolume'),
    path('nextTrack', views.nextTrack, name='nextTrack'),
    path('previousTrack', views.previousTrack, name='previousTrack')
]