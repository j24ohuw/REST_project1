from django.http import Http404
from django.contrib.auth.models import User
from django.utils import timezone
from stocks.models import Stock, Position
from stocks.serializers import StockSerializer, PositionSerializer#, UserSerializer
from django.core.exceptions import MultipleObjectsReturned
import stocks.ERC as ERC

from rest_framework import viewsets #mixins
from rest_framework import renderers
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from stocks.permissions import IsOwnerOrReadOnly

from tiingo import TiingoClient
import numpy as np
import datetime

client = TiingoClient({'api_key':"9010cf77d64c7b3bce13ee565d1b95604b04c0f2"})

def hist(ticker):
    try:
        quote = client.get_ticker_price(ticker,
                     fmt='json',
                     endDate = datetime.datetime.now(),
                     startDate = datetime.datetime.now()-datetime.timedelta(days=90),
                     frequency = 'daily'
                     )
        return quote
    except Exception as e:
        raise Http404

# class PositionHighlight(generics.GenericAPIView):
#
#     queryset = Position.objects.all()
#     renderer_classes = (renderers.StaticHTMLRenderer)
#
#     def get(self, request, *args, **kwargs):
#         position = self.get_object()
#         return Response(position.highlighted)

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
        if (stock != None) and (stock.last_updated.date() == timezone.now().date()):
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        #data is either not up to date or does not exist. Call Put
        return self.post(request= request, ticker=ticker)

    def post(self, request, ticker):
        #get historical data
        quote = hist(ticker=ticker)
        #register data on a Stock instance
        stock = Stock(ticker=ticker)
        stock.price = quote[-1]['adjClose']
        stock.last_updated = timezone.now()
        serializer = StockSerializer(stock, data=request.data) #serialize stock instance
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
        prices = np.array([data['adjClose'] for data in quote])
        log_returns = np.log(prices[1:])-np.log(prices[:-1])
        variance = np.var(log_returns)
        volatility= (variance**0.5)*(252**0.5)
        return Response({'volatility': '{:.2%}'.format(volatility)})

"""
"""

@api_view(['GET'])
def position_root(request, username):
    print(username, request)
    return Response({
    'positions': reverse('position-list', kwargs={'username':username} ,request=request)
    })

class PositionList(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # lookup_field = 'owner'

    def get_queryset(self):
        if self.kwargs.get('username', None) != None:
            owner = User.objects.filter(username = self.kwargs['username'])
        else:
            owner = User.objects.first()
        return Position.objects.filter(owner=owner)

    """
    Create a new position only if the position does not exist for the same user"""
    def post(self, request, *args, **kwargs):
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

    # @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def list(self, request, *args, **kwargs):
        # if kwargs.get('username',None) != None:
        #     #first get user object given the user name
        #     owner = User.objects.get(username=kwargs['username'])
        #     #filter position list by owner
        #     queryset = self.queryset.filter(owner=owner)
        # else:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for query in serializer.data:
            ticker = query['ticker']
            stock_data = StockDetail().get(request, ticker=ticker).data
            query['price'] = stock_data['price']
        return Response(serializer.data)

    @action(detail=False)
    def get_volatility(self, request, *args, **kwargs):
        #if username is passed in kwargs filter queryset with username
        positions = self.queryset
        #pass queryset to a position serializer
        serializer = PositionSerializer(positions, many=True)
        #attach volatility
        for position in serializer.data:
            ticker = position['ticker']
            position['volatility'] = Volatility().get(request, ticker=ticker).data['volatility']
        #return data
        return Response(serializer.data)

    @action(detail=False)
    def get_volatility_weighted(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
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

    @action(detail=False)
    def get_ERC(self, request, username):
        serializer = self.get_serializer(self.queryset, many=True)
        returns = []
        for stock in serializer.data:
            #get historical price data
            quote = hist(stock['ticker'])
            prices = np.array([data['adjClose'] for data in quote])
            #compute log returns and append to the list of returns
            log_returns = np.log(prices[1:])-np.log(prices[:-1])
            returns.append(log_returns)
        #pass the log returns to compute weights of Equal Risk Contribution portfolio
        weights = ERC.construct_ERC(returns)
        for i, stock in enumerate(serializer.data):
            stock['ERC weight'] = '{:.2%}'.format(weights[i])
        return Response(serializer.data)


# class PositionDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Position.objects.all()
#     serializer_class = PositionSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,
#                       IsOwnerOrReadOnly,)
#     lookup_field = 'owner'

# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     # lookup_field = 'username'
#
# class UserDetail(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = 'username'
#
#
# class CreateUserView(CreateAPIView):
#
#     model = User
#     permission_classes = [
#         permissions.AllowAny
#     ]
#     serializer_class = UserSerializer


# class PositionDetail(generics.RetrieveUpdateDestroyAPIView):
#
# try:
#     #Request 90 days of daily price values from Tiingo
#     quote = hist(ticker)
#     #pass the values to the POST method to create a data entry
#     return self.put(request= request, ticker=ticker, quote=quote)
# except Exception as e:
#     return Response({'Error':str(e)})
