# Generated by Django 3.2.6 on 2021-08-14 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_revendedor_cpf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revendedor',
            name='cpf',
            field=models.CharField(max_length=14, unique=True),
        ),
    ]