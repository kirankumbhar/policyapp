from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.
class ComplianceFramework(models.TextChoices):
    SOC2 = 'SOC2', 'SOC2'
    # Add other compliance frameworks as needed

class EnforcementType(models.TextChoices):
    MANDATORY = 'MANDATORY', 'Mandatory'
    RECOMMENDED = 'RECOMMENDED', 'Recommended'
    OPTIONAL = 'OPTIONAL', 'Optional'

class TemplateStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    IN_REVIEW = 'IN_REVIEW', 'In Review'
    ACTIVE = 'ACTIVE', 'Active'
    ARCHIVED = 'ARCHIVED', 'Archived'

class Org(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.id} - {self.name}"

class Dept(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self)-> str:
        return f"{self.id} - {self.name}"

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=512)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    description = models.TextField()
    compliance_framework = models.CharField(
        max_length=50,
        choices=ComplianceFramework.choices,
        default=ComplianceFramework.SOC2
    )
    enforcement_type = models.CharField(
        max_length=20,
        choices=EnforcementType.choices,
        default=EnforcementType.OPTIONAL
    )

    def __str__(self)-> str:
        return f"{self.id} - {self.name}"

class DeptPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Dept Policies"

    def __str__(self):
        return f"{self.dept.name} - {self.policy.name}"

class PolicyTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    version = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=TemplateStatus.choices,
        default=TemplateStatus.DRAFT
    )
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ['policy', 'status']

    def __str__(self):
        return f"{self.policy.name} - v{self.version} ({self.status})"

class PolicyTemplateLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_template = models.ForeignKey(PolicyTemplate, on_delete=models.CASCADE)
    prev_status = models.CharField(max_length=20, choices=TemplateStatus.choices)
    curr_status = models.CharField(max_length=20, choices=TemplateStatus.choices)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)  # Added for audit purposes

    def __str__(self):
        return f"{self.policy_template} status change: {self.prev_status} -> {self.curr_status}"

class PolicyStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_template = models.ForeignKey(PolicyTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    knowledge_document = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.policy_template}"

class FieldValueType(models.TextChoices):
    NUMBER = 'NUMBER', 'Number'
    BOOLEAN = 'BOOLEAN', 'Boolean'
    STRING = 'STRING', 'String'
    DATETIME = 'DATETIME', 'DateTime'

class PolicyStepField(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_step = models.ForeignKey(PolicyStep, on_delete=models.CASCADE)  # Added this relationship
    field_name = models.CharField(max_length=255)
    field_key = models.CharField(max_length=255)
    field_value_type = models.CharField(
        max_length=20,
        choices=FieldValueType.choices,
        default=FieldValueType.STRING
    )

    def __str__(self):
        return f"{self.field_name} ({self.field_key})"

class PolicyAcknowledgment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_template = models.ForeignKey(PolicyTemplate, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    is_user_initiated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.policy_template.policy.name} - {self.user}"

class PolicyAcknowledgmentStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_acknowledgment = models.ForeignKey(PolicyAcknowledgment, on_delete=models.CASCADE)
    policy_step = models.ForeignKey(PolicyStep, on_delete=models.CASCADE)
    step_report_document = models.CharField(max_length=512, null=True, blank=True)
    is_acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.policy_acknowledgment} - {self.policy_step.name}"

class PolicyStepFieldValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_acknowledgment_step = models.ForeignKey(PolicyAcknowledgmentStep, on_delete=models.CASCADE)
    policy_step_field = models.ForeignKey(PolicyStepField, on_delete=models.CASCADE)
    field_value = models.TextField()

    def __str__(self):
        return f"{self.policy_step_field.field_name}: {self.field_value}"