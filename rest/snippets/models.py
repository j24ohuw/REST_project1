from django.db import models
from django.utils import timezone
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
# Create your models here.


LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES,
                                default='python',
                                max_length = 100)
    style = models.CharField(choices=STYLE_CHOICES,
                             default='friendly',
                             max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()
    class Meta:
        ordering=('created',)

    def save(self, *args, **kwargs):
        """
        User the pygments library to create a highlighted HTML representation
        of the code snippet
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)




# class Stock(models.Model):
#     ticker = models.CharField(default='SPY', max_length = 10)
#     price = models.FloatField(default = -1)
#     volatility = models.FloatField(default=-1)
#     last_updated = models.DateTimeField(default=timezone.now)
#     created = models.DateTimeField(default=timezone.now)
#     # data_type = models.CharField(default='adjClose', max_length = 20)
#     # start_date = models.DateTimeField(default=timezone.now)
#     # end_date = models.DateTimeField(default=timezone.now)
#     # class Meta:
#     #     ordering=('created',)
#
# class Position(models.Model):
#     ticker = models.CharField(default='SPY', max_length = 10)
#     average_cost = models.FloatField(default = -1)
#     start_date = models.DateTimeField(default=timezone.now)
#     # end_date = models.DateTimeField(default=timezone.now)
#     market_value = models.FloatField(default = -1)
#     quantity = models.IntegerField(default=0)
#     volatility = models.FloatField(default=-1)
#     owner = models.ForeignKey('auth.User', related_name='positions', on_delete=models.CASCADE)
#
#     class Meta:
#         ordering=('market_value',)
