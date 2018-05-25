# Stdlib imports
from __future__ import absolute_import
# Core Django imports
from django.conf.urls import url, include
# Third-party app imports
from rest_framework import renderers
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
# Imports from your apps
from . import views
from .views import SnippetViewSet, UserViewSet, api_root


# urlpatterns = [
#     url(r'^$', views.api_root),
#
#     url(r'^snippets/$',
#         views.SnippetList.as_view({'get':'list'}),
#         ),
#
#     url(r'^snippets/(?P<username>[\w]+)/$',
#         views.SnippetList.as_view({'get':'owner_list',}),
#         name='snippet-list'),
#
#
#     url(r'^snippets/(?P<pk>[0-9]+)/$',
#         views.SnippetDetail.as_view(),
#         name='snippet-detail'),
#
#     url(r'^snippets/(?P<pk>[0-9]+)/highlight/$',
#         views.SnippetHighlight.as_view(),
#         name='snippet-highlight'),
#
#     url(r'^users/$',
#         views.UserList.as_view(),
#         name='user-list'),
#
#     url(r'^users/(?P<username>[\w]+)/$',
#         views.UserDetail.as_view(),
#         name='user-detail'),
#
#     url(r'^newuser/$',
#         views.CreateUserView.as_view(),
#         name='Register'),
# ]
# urlpatterns = format_suffix_patterns(urlpatterns)

# #create a set of views
# snippet_list = SnippetViewSet.as_view({
#     'get':'list',
#     'post': 'create'
# })
# snippet_detail = SnippetViewSet.as_view({
#     'get':'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
# snippet_highlight = SnippetViewSet.as_view({
#     'get':'highlight'}, renderer_classes=[renderers.StaticHTMLRenderer])
# user_list = UserViewSet.as_view({
#     'get':'list',
# })
# user_detail = UserViewSet.as_view({
#     'get': 'retrieve'
# })
#create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls))
]





# urlpatterns = format_suffix_patterns([
#     url(r'^$', views.api_root),
#     url(r'^snippets/$',
#         views.SnippetList.as_view(),
#         name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$',
#         views.SnippetDetail.as_view(),
#         name='snippet-detail'),
#     url(r'^snippets/(?P<pk>[0-9]+)/highlight/$',
#         views.SnippetHighlight.as_view(),
#         name='snippet-highlight'),
#     url(r'^users/$',
#         views.UserList.as_view(),
#         name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$',
#         views.UserDetail.as_view(),
#         name='user-detail')
# ])
#

# snippet_list = SnippetViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# snippet_detail = SnippetViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
# snippet_highlight = SnippetViewSet.as_view({
#     'get': 'highlight'
# }, renderer_classes=[renderers.StaticHTMLRenderer])
# user_list = UserViewSet.as_view({
#     'get': 'list'
# })
# user_detail = UserViewSet.as_view({
#     'get': 'retrieve'
# })
# urlpatterns = format_suffix_patterns([
#     url(r'^$', api_root),
#     url(r'^snippets/$', snippet_list, name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$', snippet_detail, name='snippet-detail'),
#     url(r'^snippets/(?P<pk>[0-9]+)/highlight/$', snippet_highlight, name='snippet-highlight'),
#     url(r'^users/$', user_list, name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail')
# ])
