# Generated by Django 5.1.4 on 2025-01-02 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_wishlistitem_priority_alter_wishlistitem_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlistitem',
            name='image_url',
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]
