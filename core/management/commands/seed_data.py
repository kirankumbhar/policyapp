# management/commands/seed_policies.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from core.models import (
    Org, Dept, User, Policy, PolicyTemplate, PolicyStep,
    PolicyStepField, PolicyAcknowledgment, PolicyAcknowledgmentStep,
    PolicyStepFieldValue
)

class Command(BaseCommand):
    help = 'Seeds the database with two SOC2 policies and related data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed policy data...')

        # Create Organization
        org = Org.objects.create(
            name='TechCorp Inc',
            domain='techcorp.com'
        )

        # Create Departments
        it_dept = Dept.objects.create(name='IT')
        hr_dept = Dept.objects.create(name='HR')

        # Create Users
        admin_user = User.objects.create(
            email='admin@techcorp.com',
            username='admin',
            password=make_password('admin123'),
            first_name='Admin',
            last_name='User',
            org=org,
            dept=it_dept,
            is_staff=True,
            is_superuser=True
        )

        normal_user = User.objects.create(
            email='user@techcorp.com',
            username='user',
            password=make_password('user123'),
            first_name='Normal',
            last_name='User',
            org=org,
            dept=hr_dept
        )

        # Create SOC2 Policies
        policies_data = [
            {
                'name': 'Data Access Control Policy',
                'description': 'Policy defining the procedures for controlling access to company data and systems',
                'steps': [
                    {
                        'name': 'Access Request',
                        'description': 'Submit formal access request',
                        'knowledge_document': 'docs/access-request-guide.pdf',
                        'fields': [
                            {
                                'name': 'Access Level',
                                'key': 'access_level',
                                'type': 'STRING'
                            },
                            {
                                'name': 'Request Date',
                                'key': 'request_date',
                                'type': 'DATETIME'
                            }
                        ]
                    },
                    {
                        'name': 'Manager Approval',
                        'description': 'Obtain manager approval for access',
                        'knowledge_document': 'docs/approval-process.pdf',
                        'fields': [
                            {
                                'name': 'Approval Status',
                                'key': 'is_approved',
                                'type': 'BOOLEAN'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Security Awareness Training Policy',
                'description': 'Annual security awareness training requirements for all employees',
                'steps': [
                    {
                        'name': 'Complete Training Module',
                        'description': 'Complete the online security awareness training',
                        'knowledge_document': 'docs/security-training.pdf',
                        'fields': [
                            {
                                'name': 'Completion Score',
                                'key': 'score',
                                'type': 'NUMBER'
                            }
                        ]
                    },
                    {
                        'name': 'Sign Acknowledgment',
                        'description': 'Sign the training completion acknowledgment',
                        'knowledge_document': 'docs/acknowledgment-form.pdf',
                        'fields': [
                            {
                                'name': 'Acknowledgment Date',
                                'key': 'ack_date',
                                'type': 'DATETIME'
                            }
                        ]
                    }
                ]
            }
        ]

        # Create policies and related data
        for policy_data in policies_data:
            # Create Policy
            policy = Policy.objects.create(
                name=policy_data['name'],
                org=org,
                description=policy_data['description'],
                compliance_framework='SOC2',
                enforcement_type='MANDATORY'
            )

            # Create PolicyTemplate
            template = PolicyTemplate.objects.create(
                policy=policy,
                version='1.0.0',
                status='ACTIVE',
                approved_by=admin_user
            )

            # Create Steps and Fields
            for step_data in policy_data['steps']:
                step = PolicyStep.objects.create(
                    policy_template=template,
                    name=step_data['name'],
                    description=step_data['description'],
                    knowledge_document=step_data['knowledge_document']
                )

                # Create Fields for each step
                for field_data in step_data['fields']:
                    PolicyStepField.objects.create(
                        policy_step=step,
                        field_name=field_data['name'],
                        field_key=field_data['key'],
                        field_value_type=field_data['type']
                    )

            # Create sample acknowledgment for normal user
            acknowledgment = PolicyAcknowledgment.objects.create(
                policy_template=template,
                user=normal_user,
                is_acknowledged=False,
                requested_at=timezone.now(),
                expired_at=timezone.now() + timedelta(days=30),
                is_recurring=True,
                is_user_initiated=False
            )

            # Create acknowledgment steps
            for step in template.policystep_set.all():
                PolicyAcknowledgmentStep.objects.create(
                    policy_acknowledgment=acknowledgment,
                    policy_step=step,
                    step_report_document='',
                    is_acknowledged=False
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded policy data'))