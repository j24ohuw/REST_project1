#std libs
from __future__ import absolute_import
#core django
from django.conf.urls import url, include
#third party
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
#your apps
from . import views

router = DefaultRouter()
urlpatterns = [

    url(r'^stock/(?P<ticker>[\w-]+)/$',
        views.StockDetail.as_view()
        ),

    url(r'^stock/(?P<ticker>[\w-]+)/volatility/$',
        views.Volatility.as_view()
        ),

    url(r'^users/(?P<username>[\w]+)/positions/$',
        views.PositionList.as_view({'get':'list',}),
        name='position-list'),

    url(r'^users/(?P<username>[\w]+)/positions/risk/$',
        views.PositionList.as_view({'get':'get_volatility'}),
        name='position-risk'
        ),

    url(r'^users/(?P<username>[\w]+)/positions/risk/risk_parity/$',
        views.PositionList.as_view({'get':'get_ERC',})
        ),

    url(r'^users/(?P<username>[\w]+)/positions/risk/volatility_weighted/$',
        views.PositionList.as_view({'get':'get_volatility_weighted',})
        ),

]

urlpatterns = format_suffix_patterns(urlpatterns)
