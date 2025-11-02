# Generated migration for adding use_proxy field to Website model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight_crawler', '0004_alter_website_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='use_proxy',
            field=models.BooleanField(default=False, help_text='Use proxy for this website to avoid IP bans'),
        ),
    ]
