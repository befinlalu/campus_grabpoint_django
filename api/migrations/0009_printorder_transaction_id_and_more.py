# Generated by Django 5.1.7 on 2025-03-25 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_order_transaction_id_alter_order_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='printorder',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='printorder',
            name='payment_status',
            field=models.CharField(choices=[('cod', 'Cash on Delivery'), ('upi', 'UPI Payment')], default='cod', max_length=20),
        ),
        migrations.AlterField(
            model_name='printorder',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('printed', 'Printed'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
