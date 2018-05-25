#std libs
from __future__ import absolute_import
from tiingo import TiingoClient
import numpy as np
import datetime
import urllib.request, json
import pandas as pd
#core django
from django.http import Http404
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned
#third party
from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.reverse import reverse
#your apps
from .models import Stock, Position
from .serializers import StockSerializer, PositionSerializer
from .permissions import IsOwnerOrReadOnly
from . import risk_parity

ALPHA_VANTAGE_API_KEY = 'B8NP683F4S21K639'
BASE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&'
client = TiingoClient({'api_key':"9010cf77d64c7b3bce13ee565d1b95604b04c0f2"})


def hist(ticker):
    #querry tiingo first
    try:
        quote = client.get_ticker_price(ticker,
             fmt='json',
             endDate = datetime.datetime.now(),
             startDate = datetime.datetime.now()-datetime.timedelta(days=90),
             frequency = 'daily'
             )
        prices = [data['adjClose'] for data in quote]
    except Exception as error:
        if error.__context__.response.status_code == 404:
            prices = -1
            print(error)
    #if tiingo returns a valid price, use tiingo data
    if prices != -1:
        return prices
    #querry alpha vantage
    with urllib.request.urlopen(BASE_URL+'symbol='+ticker+\
                        '&apikey='+ALPHA_VANTAGE_API_KEY) as url:
        try:
            data = json.loads(url.read().decode())['Time Series (Daily)']
            data = pd.DataFrame(data).T
            data = data['5. adjusted close'].astype(float)
            prices =  list(data)
        except:
            print('something went wrong, bubbles')
            raise Http404
    return prices

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
        if (stock != None) and \
            (stock.last_updated.date() == timezone.now().date()) and \
            (stock.price != -1):
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        #data is either not up to date or does not exist. Call Put
        return self.post(request= request, ticker=ticker)

    def post(self, request, ticker):
        #get historical data
        quote = hist(ticker=ticker)
        #register data on a Stock instance
        stock = Stock(ticker=ticker)
        if quote:
            stock.price = quote[-1]
        else:
            stock.price = -1
        stock.last_updated = timezone.now()
        #serialize stock instance
        serializer = StockSerializer(stock, data=request.data)
        if serializer.is_valid():
            #valid; return Response serializer data
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ticker, format=None):
        stocks = Stock.objects.filter(ticker=ticker)
        for stock in list(stocks)[:-1]:
            stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Volatility(StockDetail):
    def get(self, request, ticker):
        return self.post(request, ticker)

    def post(self, request, ticker):
        quote = hist(ticker)
        prices = np.array(quote)
        log_returns = np.log(prices[1:])-np.log(prices[:-1])
        variance = np.var(log_returns)
        volatility= (variance**0.5)*(252**0.5)
        return Response({'volatility': '{:.2%}'.format(volatility)})

"""
"""
class PositionList(viewsets.ModelViewSet):
    serializer_class = PositionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # lookup_field = 'owner'

    def get_queryset(self):
        if self.kwargs.get('username', None) != None:
            owner = User.objects.filter(username = self.kwargs['username'])
        else:
            owner = User.objects.first()
        return Position.objects.filter(owner=owner[0])

    """
    Create a new position only if the position does not exist for the same user"""
    def post(self, request, *args, **kwargs):
        if self.get_queryset().filter(ticker=request.data['ticker'],
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
        objects = self.get_queryset()#.filter(owner=request.user)
        for object in objects:
            object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #list user's current positions
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for query in serializer.data:
            ticker = query['ticker']
            stock_data = StockDetail().get(request, ticker=ticker).data
            query['price'] = stock_data['price']
        return Response(serializer.data)

    #list user's current positions and their volatility from log returns
    @action(detail=False)
    def get_volatility(self, request, *args, **kwargs):
        #if username is passed in kwargs filter queryset with username
        positions = self.get_queryset()
        #pass queryset to a position serializer
        serializer = PositionSerializer(positions, many=True)
        #attach volatility
        for position in serializer.data:
            ticker = position['ticker']
            position['volatility'] = Volatility().get(request, ticker=ticker).data['volatility']
        #return data
        return Response(serializer.data)

    #return list of volatility weighted portfolio
    @action(detail=False)
    def get_volatility_weighted(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        vol_arr = []
        for stock in serializer.data:
            volatility = Volatility().get(request, ticker = stock['ticker']).data['volatility']
            inverse_volatility = float(volatility[:-1])**-1
            vol_arr.append(inverse_volatility)
            # vol_arr.append(float(position['volatility'][:-1])**-1)
        weights = [i/sum(vol_arr) for i in vol_arr]
        for i, stock in enumerate(serializer.data):
            stock['1/n weight'] = '{:.2%}'.format(weights[i])
        return Response(serializer.data)

    #return list of risk parity portfolio
    @action(detail=False)
    def get_ERC(self, request, username):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        returns = []
        for stock in serializer.data:
            #get historical price data
            quote = hist(stock['ticker'])
            prices = np.array([data for data in quote])
            #compute log returns and append to the list of returns
            log_returns = np.log(prices[1:])-np.log(prices[:-1])
            returns.append(log_returns[:60])
        #pass the log returns to compute weights of Equal Risk Contribution portfolio
        weights = risk_parity.construct_ERC(returns)
        for i, stock in enumerate(serializer.data):
            stock['ERC weight'] = '{:.2%}'.format(weights[i])
        return Response(serializer.data)
