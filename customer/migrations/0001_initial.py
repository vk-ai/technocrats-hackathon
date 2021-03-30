# Generated by Django 3.0.8 on 2020-07-18 23:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=150, verbose_name='First name')),
                ('middle_name', models.CharField(blank=True, max_length=150, verbose_name='Middle name')),
                ('last_name', models.CharField(max_length=150, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=255, unique=True, verbose_name='email address')),
                ('password', models.CharField(blank=True, max_length=128, verbose_name='password')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='customers/')),
                ('date_of_birth', models.DateField(blank=True, default='')),
                ('customer_type', models.CharField(blank=True, choices=[('elite', 'Elite'), ('pro', 'Pro'), ('platinum', 'Platinum')], default='elite', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date of joining')),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Customer Profiles',
            },
        ),
        migrations.CreateModel(
            name='FCMDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.TextField(default='', verbose_name='Registration token')),
                ('type', models.CharField(choices=[('ios', 'ios'), ('android', 'android')], max_length=10)),
                ('active', models.BooleanField(default=True, help_text='Inactive devices will not be sent notifications', verbose_name='Is active')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'FCM device',
                'verbose_name_plural': 'FCM devices',
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, verbose_name='Name')),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=150, verbose_name='Category')),
                ('product_type', models.CharField(blank=True, max_length=150, verbose_name='Product Type')),
                ('prize', models.FloatField(blank=True, null=True)),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='product/')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Product Details',
            },
        ),
        migrations.CreateModel(
            name='SalesRepresentative',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=150, verbose_name='First name')),
                ('middle_name', models.CharField(blank=True, max_length=150, verbose_name='Middle name')),
                ('last_name', models.CharField(max_length=150, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=255, unique=True, verbose_name='email address')),
                ('password', models.CharField(blank=True, max_length=128, verbose_name='password')),
                ('status', models.CharField(blank=True, choices=[('available', 'Available'), ('not_available', 'Not Available')], default='available', max_length=20)),
                ('store', models.CharField(blank=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date of joining')),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Sales Representatives',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.CustomerProfile')),
            ],
            options={
                'verbose_name_plural': 'Order Details',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Orders')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Products')),
            ],
            options={
                'verbose_name_plural': 'Order Items',
            },
        ),
        migrations.CreateModel(
            name='KnownEncoding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('encoding', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date of joining')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.CustomerProfile')),
            ],
            options={
                'verbose_name_plural': 'Known Encodings',
            },
        ),
        migrations.CreateModel(
            name='FCMNotifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Message')),
                ('data_message', models.TextField(blank=True, verbose_name='extra_data')),
                ('multicast_id', models.CharField(blank=True, max_length=128, verbose_name='Multicast ID')),
                ('notification_type', models.CharField(default=None, max_length=30, null=True, verbose_name='type')),
                ('reminder', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.FCMDevice', verbose_name='Device ID')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='customer.SalesRepresentative')),
            ],
            options={
                'verbose_name': 'FCM Notification',
                'verbose_name_plural': 'FCM Notifications',
            },
        ),
        migrations.AddField(
            model_name='fcmdevice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.SalesRepresentative', verbose_name='Fcm Mobile User'),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='previous_sales_rep',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='customer.SalesRepresentative'),
        ),
        migrations.AlterUniqueTogether(
            name='fcmdevice',
            unique_together={('user', 'registration_id')},
        ),
    ]