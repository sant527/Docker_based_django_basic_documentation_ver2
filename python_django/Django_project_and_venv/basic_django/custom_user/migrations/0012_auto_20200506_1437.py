# Generated by Django 3.0.3 on 2020-05-06 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0011_auto_20200506_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$180000$tVlZVRLFqY05$nYZxFHcRwG8len5JIYywgkpUaVgUuPRyvWhZR95vU/s=', max_length=128, verbose_name='password'),
        ),
    ]
