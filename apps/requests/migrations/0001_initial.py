# Generated by Django 5.1.3 on 2024-11-26 17:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('PENDING', 'Pending'), ('ARCHIVED', 'Archived'), ('DELETED', 'Deleted')], default='ACTIVE', max_length=20)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('version', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('deactivated_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(blank=True, max_length=10, unique=True)),
                ('description', models.TextField(blank=True)),
                ('requires_approval', models.BooleanField(default=True)),
                ('approval_levels', models.PositiveIntegerField(default=1)),
                ('deactivated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deactivations', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AssetRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('version', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('deactivated_at', models.DateTimeField(blank=True, null=True)),
                ('request_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='MEDIUM', max_length=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('desired_date', models.DateField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('attachments', models.FileField(blank=True, null=True, upload_to='request_attachments/')),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asset_requests', to='assets.asset')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_asset_requests', to=settings.AUTH_USER_MODEL)),
                ('deactivated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deactivated_asset_requests', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_asset_requests', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requested_assets', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_asset_requests', to=settings.AUTH_USER_MODEL)),
                ('request_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='requests.requesttype')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RequestApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('version', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('deactivated_at', models.DateTimeField(blank=True, null=True)),
                ('approval_level', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('comments', models.TextField(blank=True)),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='request_approvals', to=settings.AUTH_USER_MODEL)),
                ('deactivated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_deactivations', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modifications', to=settings.AUTH_USER_MODEL)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='requests.assetrequest')),
            ],
            options={
                'ordering': ['approval_level', '-created_at'],
                'indexes': [models.Index(fields=['status'], name='requests_re_status_91e3cf_idx'), models.Index(fields=['approval_level'], name='requests_re_approva_d9b9c7_idx')],
                'unique_together': {('request', 'approver', 'approval_level')},
            },
        ),
        migrations.AddIndex(
            model_name='requesttype',
            index=models.Index(fields=['name'], name='requests_re_name_c6b472_idx'),
        ),
        migrations.AddIndex(
            model_name='requesttype',
            index=models.Index(fields=['code'], name='requests_re_code_9381b3_idx'),
        ),
        migrations.AddIndex(
            model_name='assetrequest',
            index=models.Index(fields=['request_id'], name='requests_as_request_124c13_idx'),
        ),
        migrations.AddIndex(
            model_name='assetrequest',
            index=models.Index(fields=['status'], name='requests_as_status_83a60e_idx'),
        ),
        migrations.AddIndex(
            model_name='assetrequest',
            index=models.Index(fields=['priority'], name='requests_as_priorit_9d3980_idx'),
        ),
        migrations.AddIndex(
            model_name='assetrequest',
            index=models.Index(fields=['desired_date'], name='requests_as_desired_3f7c0d_idx'),
        ),
    ]
