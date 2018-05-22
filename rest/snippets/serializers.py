from rest_framework import serializers
from snippets.models import LANGUAGE_CHOICES, STYLE_CHOICES, Snippet #, Stock, Position
from stocks.models import Stock, Position
from stocks.serializers import PositionSerializer
from django.contrib.auth.models import User
from django.utils import timezone


class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    positions = serializers.HyperlinkedIdentityField(view_name='position-list', lookup_field='username')
    snippets = serializers.HyperlinkedIdentityField(view_name='snippet-list', lookup_field='username')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id','username', 'password', 'url','snippets', 'positions')#, 'position_listing')
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'},
            # 'position_listing': {'lookup_field': 'username'}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# class SnippetSerializer(serializers.HyperlinkedModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')
#
#     class Meta:
#         model = Snippet
#         fields = ('url', 'id', 'highlight', 'owner',
#                   'title', 'code', 'linenos', 'language', 'style')
#
#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'snippets')


# import csv
# import os
#
# workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
# c = open(os.path.join(workpath, 'supported_tickers.csv'), 'rt')
#
# valid_tickers = set()
# with c as inputfile:
#     for row in csv.reader(inputfile):
#         if row[0] not in valid_tickers:
#             valid_tickers.add(row[0])
#
# class StockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Stock
#         fields = ('ticker', 'price', 'volatility',)
#
#     def CheckLastUpdated(self, last_updated):
#         if last_updated.date() == timezone.now():
#             return True
#
#
# class PositionSerializer(serializers.ModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     class Meta:
#         model = Position
#         fields = ('ticker','start_date','quantity','owner')
#
#     def validate_ticker(self, ticker):
#         if ticker.upper() not in valid_tickers:
#             raise serializers.ValidationError("Please provide a valid ticker name")
#         return ticker.upper()
#
#     def validate_quantity(self, quantity):
#         if quantity == 0:
#             raise serializers.ValidationError("You cannot initialize your position with 0 stock ")
#         return quantity


# from django.contrib.auth import get_user_model # If used custom user model
#
# UserModel = get_user_model()
# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     def create(self, validated_data):
#         user = UserModel.objects.create(
#             username=validated_data['username']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#
#         return user
#
#     class Meta:
#         model = UserModel

    # id = serializers.IntegerField(read_only=True)
    # title = serializers.CharField(required=False,
    #                               allow_blank=True,
    #                               max_length=100)
    # code = serializers.CharField(style={'base_template':'textarea.html'})
    # linenos = serializers.BooleanField(required=False)
    # language = serializers.ChoiceField(choices=LANGUAGE_CHOICES,
    #                                    default='python')
    # style = serializers.ChoiceField(choices=STYLE_CHOICES,
    #                               default='friendly')
    #
    #
    # def create(self, validated_data):
    #     """
    #     Create and return a new 'Snippet' instance, given the validated databases
    #     """
    #     return Snippet.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing 'Snippet' instance, given the validated data
    #     """
    #
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.linenos = validated_data.get('linenos', instance.linenos)
    #     instance.language = validated_data.get('language', instance.language)
    #     instance.style = validated_data.get('style', instance.style)
    #
    #     instance.save()
    #     return instance
