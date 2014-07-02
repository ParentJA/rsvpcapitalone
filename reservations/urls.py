from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns('',
    url(r'^api/reservations/$', 'api_reservations', name='api_reservations'),
    url(r'^api/reservations/(?P<reservation_id>\d+)/$', 'api_reservations', name='api_reservations'),
)