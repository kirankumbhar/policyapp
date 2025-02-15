# Generated by Django 5.1.6 on 2025-02-13 13:50

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dept',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Org',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('domain', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('knowledge_document', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.dept')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.org')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('compliance_framework', models.CharField(choices=[('SOC2', 'SOC2')], max_length=50)),
                ('enforcement_type', models.CharField(choices=[('MANDATORY', 'Mandatory'), ('RECOMMENDED', 'Recommended'), ('OPTIONAL', 'Optional')], max_length=20)),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.org')),
            ],
        ),
        migrations.CreateModel(
            name='DeptPolicy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.dept')),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policy')),
            ],
            options={
                'verbose_name_plural': 'Dept Policies',
            },
        ),
        migrations.CreateModel(
            name='PolicyAcknowledgment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_acknowledged', models.BooleanField(default=False)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('expired_at', models.DateTimeField(blank=True, null=True)),
                ('is_recurring', models.BooleanField(default=False)),
                ('is_user_initiated', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyAcknowledgmentStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('step_report_document', models.CharField(max_length=512)),
                ('is_acknowledged', models.BooleanField(default=False)),
                ('policy_acknowledgment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policyacknowledgment')),
                ('policy_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policystep')),
            ],
        ),
        migrations.CreateModel(
            name='PolicyStepField',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('field_name', models.CharField(max_length=255)),
                ('field_key', models.CharField(max_length=255)),
                ('field_value_type', models.CharField(choices=[('NUMBER', 'Number'), ('BOOLEAN', 'Boolean'), ('STRING', 'String'), ('DATETIME', 'DateTime')], max_length=20)),
                ('policy_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policystep')),
            ],
        ),
        migrations.CreateModel(
            name='PolicyStepFieldValue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('field_value', models.TextField()),
                ('policy_acknowledgment_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policyacknowledgmentstep')),
                ('policy_step_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policystepfield')),
            ],
        ),
        migrations.CreateModel(
            name='PolicyTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('IN_REVIEW', 'In Review'), ('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], max_length=20)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policy')),
            ],
            options={
                'unique_together': {('policy', 'status')},
            },
        ),
        migrations.AddField(
            model_name='policystep',
            name='policy_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policytemplate'),
        ),
        migrations.AddField(
            model_name='policyacknowledgment',
            name='policy_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policytemplate'),
        ),
        migrations.CreateModel(
            name='PolicyTemplateLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('prev_status', models.CharField(choices=[('DRAFT', 'Draft'), ('IN_REVIEW', 'In Review'), ('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], max_length=20)),
                ('curr_status', models.CharField(choices=[('DRAFT', 'Draft'), ('IN_REVIEW', 'In Review'), ('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], max_length=20)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('policy_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.policytemplate')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
