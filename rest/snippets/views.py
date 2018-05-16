from django.http import Http404
from django.contrib.auth.models import User

from snippets.models import Snippet #, Stock, Position
from snippets.serializers import SnippetSerializer, UserSerializer #, PositionSerializer, StockSerializer
from snippets.permissions import IsOwnerOrReadOnly

from rest_framework import mixins
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions



class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly,)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CreateUserView(CreateAPIView):

    model = User
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer



# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework.generics import DestroyModelMixin


# from tiingo import TiingoClient
# import numpy as np
# import datetime
#
# client = TiingoClient({'api_key':"9010cf77d64c7b3bce13ee565d1b95604b04c0f2"})
# class PositionList(generics.ListCreateAPIView):
#     queryset = Position.objects.all()
#     serializer_class = PositionSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#
#     def create(self, request, *args, **kwargs):
#         """
#         Create a new position only if the position does not exist for the same user
#         """
#         serializer = self.get_serializer(data=request.data)
#         if self.queryset.filter(ticker=request.data['ticker'],
#                                 owner=request.user).exists():
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if serializer.is_valid():
#             ticker = request.data['ticker'].upper()
#             serializer.save(owner=self.request.user, ticker=ticker)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, *args, **kwargs):
#         objects = self.queryset.filter(owner=request.user)
#         for object in objects:
#             object.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.queryset.filter(owner=request.user)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#
#
#
# class StockDetail(APIView):
#     def get(self, request, ticker, format=None):
#         try:
#             #Request 90 days of daily price values from Tiingo
#             quote = client.get_ticker_price(ticker,
#                      fmt='json',
#                      endDate = datetime.datetime.now(),
#                      startDate = datetime.datetime.now()-datetime.timedelta(days=90),
#                      frequency = 'daily'
#                      )
#             #pass the values to the POST method to create a data entry
#             return self.put(request= request, ticker=ticker, quote=quote)
#         except Exception as e:
#             return Response({'Error':str(e)})
#
#     def put(self, request, ticker, quote):
#         stock = Stock(ticker=ticker)
#         stock.price = quote[-1]['adjClose']
#         stock.volatility = float(self.volatility(quote))
#         serializer = StockSerializer(stock, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def volatility(self, quote):
#         prices = np.array([data['adjClose'] for data in quote])
#         log_returns = np.log(prices[1:])-np.log(prices[:-1])
#         variance = np.var(log_returns)
#         return (variance**0.5)*(252**0.5)

# class PositionDetail(APIView):
#     def put(self, request, ticker):
#         position = Position(ticker=ticker)
#         serializer = PositionSerializer(position, request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class Position(APIView):

# class SnippetList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   mixins.GenericAPIView):
#
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
#

# class SnippetDetail(mixins.RetrieveModelMixin,
#                     mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin,
#                     generics.GenericAPIView):
#
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *argss, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
# Create your views here.
"""
class SnippetList(APIView):
    def get(self, request, format=None):
        snippets =Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SnippeDetail(APIView):
    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)##
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400HTTP_400_BAD_REQUEST)
"""
#
#
#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204HTTP_204_NO_CONTENT)


# # @api_view(['GET', 'POST'])
# def snippet_list(request,format=None):
#     """
#     List all snippets, or create a new snippet.
#     """
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
#
#     elif request.method == "POST":
#         # data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['GET','PUT','DELETE'])
# def snippet_detail(request, pk, format=None):
#     """
#     Retrieve, update or delete a code snippet.
#     """
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return RESPONSE(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         # data = JSONParser().parse(request)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
