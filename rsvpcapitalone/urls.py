from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reservations/', include('reservations.urls', namespace='reservations.urls')),
    url(r'^$', 'reservations.views.home', name='home'),
)
