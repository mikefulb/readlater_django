import datetime
from functools import partial

from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


# class Rank(models.Model):
#     """Rank of article relative to others in order of priority to read (high = read sooner)."""
#     rank = models.FloatField(help_text='Rank of article - higher value means read sooner.')
#
#     def __str__(self):
#         return f'{self.rank}'


class Category(models.Model):
    """Article categories definitions."""
    name = models.CharField(max_length=100, help_text='Category name.')

    # FIXME might be nice to add parent or children fields so we can represent a hierarchy of categories

    def __str__(self):
        return f'{self.name}'


class Article(models.Model):
    """
    Model definition for an article to be read later.

    Explanation of 'rank'' field:
      To allow the articles to be re-ordered by the user the 'rank' field with lower rank meaning
      the article should be closer to the top of the viewable list.

    """
    PRIORITY_HIGHER = 0
    PRIORITY_HIGH = 100
    PRIORITY_NORMAL = 200
    PRIORITY_LOW = 300
    PRIORITY_LOWER = 400
    PRIORITY_CHOICES = ((PRIORITY_LOWER, 'Lower'), (PRIORITY_LOW, 'Low'), (PRIORITY_NORMAL, 'Normal'),
                        (PRIORITY_HIGH, 'High'), (PRIORITY_HIGHER, 'Higher'))

    name = models.CharField(max_length=100, unique=True, help_text='Name of article.')
    notes = models.CharField(max_length=100, blank=True, help_text='Notes about article.')
    url = models.URLField(max_length=200, help_text='URL for article.')
    category = models.ForeignKey(Category, related_name='article', on_delete=models.SET(1),
                                 help_text='Article category.')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, help_text='Article priority.')
    progress = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text='Percentage progress reading article.')
    datetime_now_utc = partial(datetime.datetime.now, tz=datetime.timezone.utc)
    added_time = models.DateTimeField(default=datetime_now_utc,
                                      help_text='Timestamp for when article was added.')
    finished_time = models.DateTimeField(null=True, blank=True, editable=False,
                                         help_text='Timestamp for when article was finished.')
    updated_time = models.DateTimeField(null=True, blank=True, editable=False,
                                        help_text='Timestamp for when progress was updated.')

    def get_absolute_url(self):
        """ Default URL for display contents. """
        return reverse('article_list')

    def __str__(self):
        return f'{self.name} - {self.category} - {self.get_priority_display()} - {self.progress}'
