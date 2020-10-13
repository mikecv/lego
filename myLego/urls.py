from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^colours$', views.colours, name='colours'),
    url(r'^getcols$', views.getcols, name='getcols'),
    url(r'^parts$', views.parts, name='parts'),
    url(r'^part/(?P<code>.+)$', views.partdetails, name='partdetails'),
    url(r'^myparts$', views.myparts, name='myparts'),
    url(r'^sets$', views.sets, name='sets'),
    url(r'^set/(?P<code>.+)$', views.setdetails, name='setdetails'),
    url(r'^addset$', views.addset, name='addset'),
    url(r'^badfunc/(?P<status>.+)$', views.badfunc, name='badfunc')
]