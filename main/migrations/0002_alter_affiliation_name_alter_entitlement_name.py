# Generated by Django 4.0.8 on 2022-10-12 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='entitlement',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
