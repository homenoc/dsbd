# Generated by Django 4.2.7 on 2023-11-26 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import dsbd.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('title', models.CharField(max_length=250, verbose_name='title')),
                ('body', dsbd.models.MediumTextField(blank=True, default='', verbose_name='内容')),
                ('is_template', models.BooleanField(default=False, verbose_name='templateチケット')),
                ('is_solved', models.BooleanField(default=False, verbose_name='解決済み')),
                ('is_approve', models.BooleanField(default=False, verbose_name='承認済み')),
                ('is_reject', models.BooleanField(default=False, verbose_name='拒否済み')),
                ('from_admin', models.BooleanField(default=False, verbose_name='運営委員から起票')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='custom_auth.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'チケット',
                'verbose_name_plural': 'チケット',
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='作成日')),
                ('body', dsbd.models.MediumTextField(blank=True, default='', verbose_name='内容')),
                ('is_admin', models.BooleanField(default=False, verbose_name='運営委員がコメント')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='custom_auth.group')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.ticket')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'チャット',
                'verbose_name_plural': 'チャット',
            },
        ),
    ]