# Generated by Django 3.2.4 on 2021-08-10 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_holiday', models.DateField()),
                ('end_holiday', models.DateField()),
                ('description', models.CharField(blank=True, default=None, max_length=192, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='another_reason',
            field=models.TextField(default=None),
        ),
    ]
