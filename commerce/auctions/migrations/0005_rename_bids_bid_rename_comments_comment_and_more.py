# Generated by Django 4.0.4 on 2022-04-25 21:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_bids_endtime_alter_comments_datetime_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Bids',
            new_name='Bid',
        ),
        migrations.RenameModel(
            old_name='Comments',
            new_name='Comment',
        ),
        migrations.RenameModel(
            old_name='Listings',
            new_name='Listing',
        ),
    ]
