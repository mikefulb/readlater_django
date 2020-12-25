from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse

from readlater.models import Article, Category


class CategoryModelTest(TestCase):

    TEST_CATEGORY_NAME = 'TestCategory'

    @classmethod
    def setUpTestData(cls):
        # create a record in database - due to initial record being
        # created by migrate script this record will have an ID of 2
        Category.objects.create(name=CategoryModelTest.TEST_CATEGORY_NAME)

    def test_migrate_uncat_record(self):
        # make sure migration script created the 'Uncategorized' record
        # as the first record in database
        categ = Category.objects.get(id=1)
        self.assertEqual(categ.name, 'Uncategorized')

    def test_name_label(self):
        categ = Category.objects.get(id=2)
        field_label = categ._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_created(self):
        categ = Category.objects.get(id=2)
        self.assertEqual(categ.name, CategoryModelTest.TEST_CATEGORY_NAME)

    def test_name_maxlen(self):
        categ = Category.objects.get(id=2)
        max_length = categ._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)


class ArticleModelTest(TestCase):

    TEST_ARTICLE_NAME = 'TestArticleName'
    TEST_ARTICLE_NOTE = 'TestNotes'
    TEST_ARTICLE_URL = 'http://testurl.org'
    TEST_ARTICLE_PRIORITY = 200
    TEST_ARTICLE_PROGRESS = 100
    TEST_ARTICLE_ADDED = datetime(2020, 12, 1, 10, 20, 30, 0, tzinfo=timezone.utc)
    TEST_ARTICLE_FINISHED = datetime(2020, 12, 2, 10, 20, 30, 0, tzinfo=timezone.utc)
    TEST_ARTICLE_UPDATED = TEST_ARTICLE_FINISHED

    @classmethod
    def setUpTestData(cls):
        # load uncategorized category record which was created during migration
        uncat = Category.objects.get(id=1)
        Article.objects.create(name=ArticleModelTest.TEST_ARTICLE_NAME,
                               notes=ArticleModelTest.TEST_ARTICLE_NOTE,
                               url=ArticleModelTest.TEST_ARTICLE_URL,
                               category=uncat,
                               priority=ArticleModelTest.TEST_ARTICLE_PRIORITY,
                               progress=ArticleModelTest.TEST_ARTICLE_PROGRESS,
                               added_time=ArticleModelTest.TEST_ARTICLE_ADDED,
                               updated_time=ArticleModelTest.TEST_ARTICLE_FINISHED,
                               finished_time=ArticleModelTest.TEST_ARTICLE_UPDATED,
                               )

    def test_field_label(self):
        fields = dict(name='name',
                      notes='notes',
                      url='url',
                      category='category',
                      priority='priority',
                      progress='progress',
                      added_time='added time',
                      finished_time='finished time',
                      updated_time='updated time',
                      )

        art = Article.objects.get(id=1)
        for k, v in fields.items():
            field_label = art._meta.get_field(k).verbose_name
            self.assertEqual(field_label, v)

    def test_name_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.name, ArticleModelTest.TEST_ARTICLE_NAME)

    def test_name_maxlen(self):
        art = Article.objects.get(id=1)
        max_length = art._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_notes_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.notes, ArticleModelTest.TEST_ARTICLE_NOTE)

    def test_notes_maxlen(self):
        art = Article.objects.get(id=1)
        max_length = art._meta.get_field('notes').max_length
        self.assertEqual(max_length, 100)

    def test_url_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.url, ArticleModelTest.TEST_ARTICLE_URL)

    def test_url_maxlen(self):
        art = Article.objects.get(id=1)
        max_length = art._meta.get_field('url').max_length
        self.assertEqual(max_length, 200)

    def test_progress_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.progress, ArticleModelTest.TEST_ARTICLE_PROGRESS)

    def test_priority_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.priority, ArticleModelTest.TEST_ARTICLE_PRIORITY)

    def test_added_time_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.added_time, ArticleModelTest.TEST_ARTICLE_ADDED)

    def test_finished_time_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.finished_time, ArticleModelTest.TEST_ARTICLE_FINISHED)

    def test_updated_time_created(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.updated_time, ArticleModelTest.TEST_ARTICLE_UPDATED)

    def test_get_absolute_url(self):
        art = Article.objects.get(id=1)
        self.assertEqual(art.get_absolute_url(), reverse('article_list'))
