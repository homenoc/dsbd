# Generated by Django 5.0.3 on 2024-03-31 16:12

import dsbd.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ip',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, unique=True, verbose_name='IP Address'),
        ),
        migrations.AlterField(
            model_name='ip',
            name='use_case',
            field=dsbd.models.MediumTextField(blank=True, default='', verbose_name='使用用途'),
        ),
        migrations.AlterField(
            model_name='jpnicuser',
            name='fax',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='fax'),
        ),
    ]
