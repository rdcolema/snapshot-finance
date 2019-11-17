from django.conf.urls import include, url
from django.contrib import admin

from home import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^analysis/', include('analysis.urls')),
    url(r'^positions/', include('positions.urls')),
    url(r'^admin/', admin.site.urls),
]
