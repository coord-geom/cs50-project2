# Generated by Django 3.1.3 on 2020-12-10 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_auto_20201210_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(blank=True, to='auctions.Listing'),
        ),
    ]
