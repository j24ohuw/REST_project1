from django.conf.urls import url
from stocks import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^stock/(?P<ticker>[\w-]+)/$', views.StockDetail.as_view()),
    url(r'^portfolio/$', views.PositionList.as_view()),
    url(r'^(?P<username>[\w]+)/portfolio/$', views.PositionList.as_view()),
    url(r'^stock/(?P<ticker>[\w-]+)/volatility/$', views.volatility.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
