from rest_framework import serializers
from .models import Policy, Dept, DeptPolicy, PolicyTemplate, PolicyStep, TemplateStatus, PolicyAcknowledgment

class PolicyStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyStep
        fields = ["id", "name", "description", "knowledge_document"]

class PolicyTemplateReadSerializer(serializers.ModelSerializer):
    steps = PolicyStepSerializer(source='policystep_set', many=True, read_only=True)
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = PolicyTemplate
        fields = ["id", "version", "status", "approved_by", "steps"]

class PolicyTemplateCreateSerializer(serializers.ModelSerializer):
    steps = PolicyStepSerializer(many=True)
    
    class Meta:
        model = PolicyTemplate
        fields = ['version', 'steps']

    def validate(self, data):
        # For nested route, get policy_id from URL
        policy_id = self.context['view'].kwargs.get('policy_pk')
        if not policy_id and 'policy_id' not in data:
            raise serializers.ValidationError({"policy_id": "Policy ID is required"})
        
        if policy_id:
            data['policy_id'] = policy_id
            
        return data
        
    def validate_policy_id(self, value):
        try:
            policy = Policy.objects.get(
                id=value,
                org=self.context['request'].user.org
            )
            return policy.id
        except Policy.DoesNotExist:
            raise serializers.ValidationError("Invalid policy ID")

    def validate_version(self, value):
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', value):
            raise serializers.ValidationError(
                "Version must follow semantic versioning (e.g., 1.0.0)"
            )
        return value

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        policy_id = validated_data.pop('policy_id')
        
        template = PolicyTemplate.objects.create(
            policy_id=policy_id,
            status='DRAFT',
            **validated_data
        )
        
        for step_data in steps_data:
            fields_data = step_data.pop('fields', [])
            step = PolicyStep.objects.create(
                policy_template=template,
                **step_data
            )
            
            for field_data in fields_data:
                PolicyStepField.objects.create(
                    policy_step=step,
                    **field_data
                )
        
        return template

    
class PolicyTemplateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyTemplate
        fields = ['approved_by']
        
    def validate(self, attrs):
        template = self.instance
        
        if template.status != TemplateStatus.DRAFT:
            raise serializers.ValidationError(
                "Only templates in DRAFT status can be activated"
            )
            
        user = attrs["approved_by"]
        if not user:
            raise serializers.ValidationError(
                "Approved by cannot be null"
            )
            
        return attrs


class PolicySerializer(serializers.ModelSerializer):
    active_template = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = ["id", "name", "org", "description", "compliance_framework", "enforcement_type", "active_template"]

    def get_active_template(self, obj):
        active_template = obj.policytemplate_set.filter(status="ACTIVE").first()
        return PolicyTemplateReadSerializer(active_template).data if active_template else None
    
class PolicyAcknowledgmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyAcknowledgment
        fields = '__all__'
        read_only_fields = ('id', 'acknowledged_at', 'requested_at')


class DeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dept
        fields = ['id', 'name']

class DeptPolicySerializer(serializers.ModelSerializer):
    dept = DeptSerializer(read_only=True)
    policy = PolicySerializer(read_only=True)
    dept_id = serializers.UUIDField(write_only=True)
    policy_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = DeptPolicy
        fields = ['id', 'dept', 'policy', 'dept_id', 'policy_id']

    def validate(self, data):
        """
        Check that the dept and policy exist
        """
        try:
            dept = Dept.objects.get(id=data['dept_id'])
            policy = Policy.objects.get(id=data['policy_id'])
        except Dept.DoesNotExist:
            raise serializers.ValidationError({"dept_id": "Department does not exist"})
        except Policy.DoesNotExist:
            raise serializers.ValidationError({"policy_id": "Policy does not exist"})
            
        # Check if the combination already exists
        if DeptPolicy.objects.filter(dept=dept, policy=policy).exists():
            raise serializers.ValidationError("This department-policy combination already exists")
            
        return data
