from rest_framework import serializers
from stocks.models import Stock, Position
from django.contrib.auth.models import User
from django.utils import timezone

import csv
import os

workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
c = open(os.path.join(workpath, 'supported_tickers.csv'), 'rt')

valid_tickers = set()
with c as inputfile:
    for row in csv.reader(inputfile):
        if row[0] not in valid_tickers:
            valid_tickers.add(row[0])


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('ticker', 'price', 'volatility','last_updated',)

    def validate_ticker(self, ticker):
        if ticker.upper() not in valid_tickers:
            raise serializers.ValidationError("Please provide a valid ticker name")
        return ticker.upper()

    def to_representation(self, obj):
        # get the original representation
        ret = super(StockSerializer, self).to_representation(obj)
        ret.pop('last_updated')
        return ret
        # remove 'url' field if mobile request
        # if is_mobile_platform(self.context.get('request', None)):
        #     ret.pop('url')

        # here write the logic to check whether `elements` field is to be removed
        # pop 'elements' from 'ret' if condition is True

        # return the modified representation


class PositionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Position
        fields = ('ticker', 'owner',)#'weight', 'price', 'volatility',)

    def validate_ticker(self, ticker):
        if ticker.upper() not in valid_tickers:
            raise serializers.ValidationError("Please provide a valid ticker name")
        return ticker.upper()

    def validate_quantity(self, quantity):
        if quantity == 0:
            raise serializers.ValidationError("You cannot initialize your position with 0 stock ")
        return quantity
