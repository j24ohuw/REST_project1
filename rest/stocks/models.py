from django.db import models
from django.utils import timezone


class Stock(models.Model):
    ticker = models.CharField(default='SPY', max_length = 10)
    price = models.FloatField(default = -1)
    volatility = models.FloatField(default=-1)
    last_updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now)
    # returns = models.ListField(default =[])
    # data_type = models.CharField(default='adjClose', max_length = 20)
    # start_date = models.DateTimeField(default=timezone.now)
    # end_date = models.DateTimeField(default=timezone.now)
    # class Meta:
    #     ordering=('created',)

class Position(models.Model):
    ticker = models.CharField(default='SPY', max_length = 10)
    weight = models.FloatField(default=-1)
    average_cost = models.FloatField(default = -1)
    start_date = models.DateTimeField(default=timezone.now)
    market_value = models.FloatField(default = -1)
    quantity = models.IntegerField(default=0)
    volatility = models.FloatField(default=-1)
    owner = models.ForeignKey('auth.User', related_name='positions', on_delete=models.CASCADE)
    # end_date = models.DateTimeField(default=timezone.now)
    price = models.FloatField(default = -1)

    class Meta:
        ordering=('market_value',)
