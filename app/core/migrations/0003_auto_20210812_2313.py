# Generated by Django 3.2.6 on 2021-08-12 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210812_2238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='revendedor',
            name='name',
            field=models.CharField(default='abc', max_length=255),
            preserve_default=False,
        ),
    ]