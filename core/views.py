from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Policy, PolicyTemplate
from .serializers import PolicySerializer, PolicyTemplateSerializer

class PolicyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

class PolicyTemplateListView(generics.ListAPIView):
    """
    API endpoint to get policy templates by policy ID and status.
    URL: GET api/v1/policy/:policy_id/policytemplate?status=ACTIVE
    """
    serializer_class = PolicyTemplateSerializer

    def get_queryset(self):
        policy_id = self.kwargs.get('policy_id')

        queryset = PolicyTemplate.objects.filter(
            policy_id=policy_id
        ).select_related(
            'approved_by'
        ).prefetch_related(
            'policystep_set',
            'policystep_set__policystepfield_set'
        )
        return queryset.filter(status='ACTIVE')