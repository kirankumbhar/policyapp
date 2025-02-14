from rest_framework import serializers
from .models import Policy, PolicyTemplate, PolicyStep

class PolicyStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyStep
        fields = ["id", "name", "description", "knowledge_document"]

class PolicyTemplateSerializer(serializers.ModelSerializer):
    steps = PolicyStepSerializer(source='policystep_set', many=True, read_only=True)

    class Meta:
        model = PolicyTemplate
        fields = ["id", "version", "status", "approved_by", "steps"]

class PolicySerializer(serializers.ModelSerializer):
    active_template = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = ["id", "name", "org", "description", "compliance_framework", "enforcement_type", "active_template"]

    def get_active_template(self, obj):
        active_template = obj.policytemplate_set.filter(status="ACTIVE").first()
        return PolicyTemplateSerializer(active_template).data if active_template else None
