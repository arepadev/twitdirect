from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'adoptave.webui.views.home', name='home'),
    # url(r'^adopta/', include('adopta.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/home/guerrerocarlos/adoptave/templates/'}),
)
