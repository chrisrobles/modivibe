from django.urls import path
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.splash, name='splash'),
    path('redirectToHome', views.redirectToHome, name='redirectToHome'),
    path('webplayer', views.home, name='webplayer'),
    path('webplayer/settings', views.settings, name='webplayer/settings')
]