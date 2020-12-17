import datetime
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Rank(models.Model):
    """Rank of article relative to others in order of priority to read (high = read sooner)."""
    rank = models.FloatField(help_text='Rank of article - higher value means read sooner.')

    def __str__(self):
        return f'{self.rank}'


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
      To allow the articles to be re-ordered by the user the 'rank' field will reference a key into another
      table that maps

    """
    name = models.CharField(max_length=100, unique=True, help_text='Name of article.')
    url = models.URLField(max_length=200, help_text='URL for article.')
    category = models.ForeignKey(Category, related_name='articvle', on_delete=models.CASCADE,
                                 help_text='Article category.')
    rank = models.IntegerField(editable=False, help_text='Article rank.')
    progress = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text='Percentage progress reading article.')
    added_time = models.DateTimeField(default=datetime.datetime.now,
                                      help_text='Timestamp for when article was added.')
    finished_time = models.DateTimeField(null=True, blank=True, editable=False,
                                         help_text='Timestamp for when article was finished.')
    updated_time = models.DateTimeField(null=True, blank=True, editable=False,
                                        help_text='Timestamp for when progress was updated.')

    def get_absolute_url(self):
        """Default URL for display contents."""
        return reverse('article_list')

    def __str__(self):
        return f'{self.name} - {self.category} - {self.rank} - {self.progress}'
