# Generated by Django 4.1.10 on 2023-08-25 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_relations2', '0002_relation_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relation',
            name='metadata',
            field=models.JSONField(editable=False, null=True),
        ),
    ]
