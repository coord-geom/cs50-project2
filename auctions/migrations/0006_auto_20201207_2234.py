# Generated by Django 3.1.3 on 2020-12-07 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20201207_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='listings',
        ),
        migrations.AddField(
            model_name='listing',
            name='categories',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='auctions.category'),
        ),
    ]
