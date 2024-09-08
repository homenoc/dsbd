# Generated by Django 5.1.1 on 2024-09-08 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_auth', '0004_group_users_alter_user_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='status',
            field=models.IntegerField(choices=[(1, '有効'), (10, 'ユーザより廃止'), (11, '運営委員より廃止'), (12, '審査落ち')], default=1, verbose_name='ステータス'),
        ),
    ]
