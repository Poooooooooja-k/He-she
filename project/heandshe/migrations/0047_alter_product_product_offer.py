# Generated by Django 4.2.3 on 2023-11-08 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heandshe', '0046_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_offer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
