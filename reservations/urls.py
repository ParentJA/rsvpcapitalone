from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = patterns('reservations.views',
    url(r'^api/reservations$', 'api_reservations', name='api_reservations'),
    url(r'^api/reservations/(?P<reservation_id>\d+)/$', 'api_reservations', name='api_reservations'),
    url(r'^views/thank-you-modal.html$', TemplateView.as_view(template_name='views/thank-you-modal.html')),
    url(r'^views/waitlist-modal.html$', TemplateView.as_view(template_name='views/waitlist-modal.html')),
)