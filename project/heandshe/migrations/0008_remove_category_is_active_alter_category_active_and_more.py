# Generated by Django 4.2.3 on 2023-11-17 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heandshe', '0007_alter_product_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='category',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sub_category',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
