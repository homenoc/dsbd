# Generated by Django 5.0.3 on 2024-03-28 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_auth', '0002_user_display_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='add_service',
            new_name='allow_service_add',
        ),
        migrations.RemoveField(
            model_name='group',
            name='address_en',
        ),
        migrations.AddField(
            model_name='group',
            name='address_jp',
            field=models.CharField(default='', max_length=250, verbose_name='住所(Japanese)'),
        ),
        migrations.AddField(
            model_name='user',
            name='allow_group_add',
            field=models.BooleanField(default=True, verbose_name='グループ追加許可'),
        ),
    ]
