# Generated by Django 5.1.7 on 2025-03-12 14:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_cart_cartlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='added_at',
            new_name='created_at',
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='cart',
            name='is_checked_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cart',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='api.product'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='CartList',
        ),
    ]
