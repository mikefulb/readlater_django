# Generated by Django 3.1.4 on 2020-12-20 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readlater', '0007_article_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='rank',
            field=models.IntegerField(editable=False, help_text='Article rank.'),
        ),
    ]
