# Generated by Django 5.1.1 on 2024-09-13 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip', '0004_alter_jpnicuser_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jpnicuser',
            name='is_active',
        ),
        migrations.AddField(
            model_name='jpnicuser',
            name='is_pass',
            field=models.BooleanField(default=True, verbose_name='審査OK'),
        ),
    ]
