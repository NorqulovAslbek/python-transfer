# Generated by Django 5.2 on 2025-04-16 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(blank=True, max_length=16, null=True)),
                ('expire', models.CharField(blank=True, max_length=5, null=True)),
                ('phone', models.CharField(blank=True, max_length=12, null=True)),
                ('status', models.CharField(blank=True, max_length=10, null=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True)),
            ],
        ),
    ]
