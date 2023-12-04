# Generated by Django 4.2.7 on 2023-11-19 13:54

from django.db import migrations, models
import django.utils.timezone
import dsbd.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='作成日')),
                ('start_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='通知開始日')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='通知終了日')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('type1', models.CharField(choices=[('サービス情報', 'サービス情報'), ('その他', 'その他')], max_length=200, verbose_name='type1')),
                ('title', models.CharField(max_length=250, verbose_name='title')),
                ('body', dsbd.models.MediumTextField(blank=True, default='', verbose_name='内容')),
                ('is_important', models.BooleanField(default=False, verbose_name='重要')),
                ('is_fail', models.BooleanField(default=False, verbose_name='障害')),
                ('is_info', models.BooleanField(default=False, verbose_name='情報')),
            ],
            options={
                'ordering': ('-end_at',),
            },
        ),
    ]