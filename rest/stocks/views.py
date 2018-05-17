from django.contrib.auth.models import User
from django.utils import timezone
from stocks.models import Stock, Position
from stocks.serializers import StockSerializer, PositionSerializer
from django.core.exceptions import MultipleObjectsReturned

# from stocks.permissions import IsOwnerOrReadOnly

from rest_framework import mixins
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions

from tiingo import TiingoClient
import numpy as np
import datetime

client = TiingoClient({'api_key':"9010cf77d64c7b3bce13ee565d1b95604b04c0f2"})

class StockDetail(APIView):

    def get_object(self, ticker):
        try:
            return Stock.objects.filter(ticker=ticker).last()
        except Stock.DoesNotExist:
            return None

    def get(self, request, ticker, format=None):
        #If the stock already exists and it has already been updated today,
        #then simply return object response
        stock = self.get_object(ticker)
        # print(Stock.objects.all())
        if (stock != None) and (stock.last_updated.date() == timezone.now().date()):
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        #data is either not up to date or does not exist. Call Put
        try:
            #Request 90 days of daily price values from Tiingo
            quote = client.get_ticker_price(ticker,
                     fmt='json',
                     endDate = datetime.datetime.now(),
                     startDate = datetime.datetime.now()-datetime.timedelta(days=90),
                     frequency = 'daily'
                     )
            #pass the values to the POST method to create a data entry
            return self.put(request= request, ticker=ticker, quote=quote)
        except Exception as e:
            return Response({'Error':str(e)})

    def put(self, request, ticker, quote):
        stock = Stock(ticker=ticker)
        stock.price = quote[-1]['adjClose']
        stock.volatility = float(self.volatility(quote))
        stock.last_updated = timezone.now()
        serializer = StockSerializer(stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def volatility(self, quote):
        prices = np.array([data['adjClose'] for data in quote])
        log_returns = np.log(prices[1:])-np.log(prices[:-1])
        variance = np.var(log_returns)
        anual_volaility= (variance**0.5)*(252**0.5)
        return anual_volaility

    def delete(self, request, ticker, format=None):
        stocks = Stock.objects.filter(ticker=ticker)
        for stock in list(stocks)[:-1]:
            stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



"""
"""
class PositionList(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'username'
    """
    Create a new position only if the position does not exist for the same user"""
    def create(self, request, *args, **kwargs):
        if self.queryset.filter(ticker=request.data['ticker'],
                                owner=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ticker = request.data['ticker'].upper()
            serializer.save(owner=self.request.user, ticker=ticker)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    Only delete current user's list of stocks"""
    def delete(self, request, *args, **kwargs):
        objects = self.queryset.filter(owner=request.user)
        for object in objects:
            object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        for query in serializer.data:
            ticker = query['ticker']
            stock_data = StockDetail().get(request, ticker=ticker).data
            query['price'] = stock_data['price']
            query['volatility'] = stock_data['volatility']
        data = self.get_weights(serializer.data)
        # temp = PositionSerializer(data=data,many=True)
        # print(temp.is_valid())
        # if temp.is_valid():
        #     temp.save(data=data)
        #     print(temp.data)
        return Response(serializer.data)

    def get_weights(self, data):
        vol_arr = []
        for position in data:
            vol_arr.append(position['volatility']**-1)
        weights = [i/sum(vol_arr) for i in vol_arr]
        for i, position in enumerate(data):
            position['weight'] = weights[i]
        return data
# class PositionDetail():
#
