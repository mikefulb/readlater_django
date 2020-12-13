# Generated by Django 3.1.4 on 2020-12-13 16:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Category name.', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.FloatField(help_text='Rank of article - higher value means read sooner.')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of article.', max_length=100)),
                ('url', models.CharField(help_text='URL for article.', max_length=200)),
                ('progress', models.IntegerField(default=0, help_text='Percentage progress reading article.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('added_time', models.DateTimeField(help_text='Timestamp for when article was added.')),
                ('finished_time', models.DateTimeField(help_text='Timestamp for when article was finished.')),
                ('updated_time', models.DateTimeField(help_text='Timestamp for when progress was updated.')),
                ('category', models.ForeignKey(help_text='Article category.', on_delete=django.db.models.deletion.CASCADE, to='readlater.category')),
                ('rank', models.ForeignKey(help_text='Article rank.', on_delete=django.db.models.deletion.CASCADE, to='readlater.rank')),
            ],
        ),
    ]
