# Generated by Django 4.1.10 on 2023-08-20 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_relations2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='relation',
            name='metadata',
            field=models.JSONField(null=True),
        ),
    ]
