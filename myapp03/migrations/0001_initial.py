# Generated by Django 4.2.6 on 2023-10-23 11:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('writer', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('hit', models.IntegerField(default=0)),
                ('post_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('filename', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('filesize', models.IntegerField(default=0)),
                ('down', models.ImageField(default=0, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('writer', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('post_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp03.board')),
            ],
        ),
    ]
