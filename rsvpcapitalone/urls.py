__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Third-party library imports...
from rest_framework.urlpatterns import format_suffix_patterns

# Django imports...
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reservations/', include('reservations.urls', namespace='reservations.urls')),
    url(r'^$', 'reservations.views.home', name='home'),
)

urlpatterns += format_suffix_patterns(patterns('',
    url(r'^api/v1/', include('reservations.urls')),
))

urlpatterns += patterns('',
    url(r'^views/thank_you_modal.html$', TemplateView.as_view(template_name='views/thank_you_modal.html')),
    url(r'^views/wait_list_modal.html$', TemplateView.as_view(template_name='views/wait_list_modal.html')),
)