# Generated by Django 4.2.3 on 2023-10-25 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heandshe', '0043_alter_coupon_coupon_code_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='banner/')),
                ('description', models.CharField(max_length=100)),
            ],
        ),
    ]