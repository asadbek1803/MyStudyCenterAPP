# Generated by Django 5.1.1 on 2024-09-26 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reklamalar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', models.FileField(upload_to='images/reklamalar/')),
                ('url', models.URLField(blank=True, null=True)),
                ('added_at', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Reklamalar',
                'verbose_name_plural': 'Reklamalar',
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('about', models.TextField()),
            ],
            options={
                'verbose_name': 'Xizmatlar',
                'verbose_name_plural': 'Xizmatlar',
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.CharField(max_length=200)),
                ('company', models.CharField(default='My Study Center', max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='vacancy/images/')),
                ('day_time', models.CharField(max_length=200)),
                ('about', models.TextField()),
                ('contact', models.URLField()),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Vakansiyalar',
                'verbose_name_plural': 'Vakansiyalar',
                'ordering': ['-price'],
            },
        ),
    ]
