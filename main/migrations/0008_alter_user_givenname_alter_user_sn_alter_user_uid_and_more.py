# Generated by Django 4.0.8 on 2023-08-11 10:38

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_user_cn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='givenName',
            field=models.CharField(blank=True, help_text="Maps to 'givenName' in the UU IdP.", max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sn',
            field=models.CharField(blank=True, help_text="Maps to 'uuPrefixedSn' in the UU IdP.", max_length=150, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='uid',
            field=models.CharField(help_text="In UU terminology this is the Solis-ID, thus equal to username. Maps to 'uuShortID' in the UU IdP.", max_length=150, unique=True, verbose_name='uid'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text="Username used to log in. Best to keep the same as 'uid'", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
        migrations.CreateModel(
            name='UserOU',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
