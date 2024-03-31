# Generated by Django 5.0.3 on 2024-03-31 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('custom_auth', '0004_group_users_alter_user_groups'),
        ('ip', '0001_initial'),
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ip',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='IPService', to='service.service'),
        ),
        migrations.AddField(
            model_name='ipjpnicuser',
            name='ip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ip.ip'),
        ),
        migrations.AddField(
            model_name='jpnicuser',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom_auth.group'),
        ),
        migrations.AddField(
            model_name='jpnicuser',
            name='ip',
            field=models.ManyToManyField(blank=True, related_name='jpnic_set', through='ip.IPJPNICUser', to='ip.ip'),
        ),
        migrations.AddField(
            model_name='ipjpnicuser',
            name='jpnic_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ip.jpnicuser'),
        ),
        migrations.AddField(
            model_name='ip',
            name='jpnic_user',
            field=models.ManyToManyField(blank=True, related_name='jpnic_user_set', through='ip.IPJPNICUser', to='ip.jpnicuser'),
        ),
        migrations.AlterUniqueTogether(
            name='ipjpnicuser',
            unique_together={('jpnic_user', 'ip')},
        ),
    ]
