# Generated by Django 3.0.2 on 2020-02-02 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0005_auto_20200201_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='jwt_secret',
            field=models.UUIDField(editable=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$180000$OI0hIFNxE6YD$WJdw91qNrs+8dlbf/3eoVawmOYtxulvaHWWZ45OUg8k=', max_length=128, verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='usersessionlog',
            name='jwt_secret',
            field=models.UUIDField(editable=False),
        ),
    ]
