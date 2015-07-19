__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Django imports...
from django.conf.urls import patterns, url

# Local imports...
# from .apis import ReservationView
from .apis import ReservationViewSet


urlpatterns = patterns('reservations.apis',
    url(r'^reservations/$', ReservationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    url(r'^reservations/(?P<pk>\d+)/$', ReservationViewSet.as_view({
        'get': 'retrieve',
        'post': 'update'
    })),
)