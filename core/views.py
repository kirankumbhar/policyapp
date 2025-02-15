from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (Policy,
                     PolicyTemplate,
                     Dept,
                     DeptPolicy,
                     User,
                     TemplateStatus,
                     PolicyTemplateLog,
                     PolicyAcknowledgment)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .serializers import (PolicySerializer,
                          DeptSerializer,
                          DeptPolicySerializer,
                          PolicyTemplateReadSerializer,
                          PolicyTemplateCreateSerializer,
                          PolicyTemplateUpdateSerializer,
                          PolicyAcknowledgmentSerializer)

class PolicyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

class PolicyTemplateViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action in ['create']:
            return PolicyTemplateCreateSerializer
        return PolicyTemplateReadSerializer

    def get_policy(self):
        policy_id = self.kwargs.get('policy_pk')
        if policy_id:
            return get_object_or_404(
                Policy.objects.all(),
                id=policy_id
            )
        return None

    def get_queryset(self):
        queryset = PolicyTemplate.objects.select_related(
            'approved_by'
        ).prefetch_related(
            'policystep_set',
            'policystep_set__policystepfield_set'
        )

        policy = self.get_policy()
        if policy:
            queryset = queryset.filter(policy_id=policy.id)

        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param.upper() not in dict(PolicyTemplate._meta.get_field('status').choices):
                raise ValidationError({'status': 'Invalid status value'})
            queryset = queryset.filter(status=status_param.upper())
        else:
            if self.action in ['list', 'retrieve']:
                queryset = queryset.filter(status=TemplateStatus.ACTIVE)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        
        response_serializer = PolicyTemplateReadSerializer(template)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], url_path='activate')
    @transaction.atomic
    def activate(self, request, *args, **kwargs):
        template = self.get_object()
        
        serializer = PolicyTemplateUpdateSerializer(
            template,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        
        active_template = PolicyTemplate.objects.filter(
            policy=template.policy,
            status=TemplateStatus.ACTIVE
        ).first()
        
        if active_template:
            PolicyTemplateLog.objects.create(
                policy_template=active_template,
                prev_status=TemplateStatus.ACTIVE,
                curr_status=TemplateStatus.ARCHIVED,
                updated_by=serializer.validated_data["approved_by"]
            )
            
            active_template.status = TemplateStatus.ARCHIVED
            active_template.save()
        
        PolicyTemplateLog.objects.create(
            policy_template=template,
            prev_status=template.status,
            curr_status=TemplateStatus.ACTIVE,
            updated_by=serializer.validated_data["approved_by"]
        )
        
        template.status = TemplateStatus.ACTIVE
        template.approved_by = serializer.validated_data["approved_by"]
        template.save()
        
        response_serializer = PolicyTemplateReadSerializer(template)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )
    
class PolicyAcknowledgmentViewSet(viewsets.ModelViewSet):
    queryset = PolicyAcknowledgment.objects.all()
    serializer_class = PolicyAcknowledgmentSerializer
    
    def create(self, request, *args, **kwargs):
        policy_id = request.data.get('policy_id')
        user = User.objects.get(id=request.data.get('user'))
        
        if not policy_id or not user:
            return Response(
                {'error': 'policy_id and user are required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            policy = get_object_or_404(Policy, id=policy_id)
            
            policy_template = PolicyTemplate.objects.filter(
                policy=policy,
                status='ACTIVE'
            ).first()
            
            if not policy_template:
                return Response(
                    {'error': 'No active policy template found for this policy'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
            existing_acknowledgment = PolicyAcknowledgment.objects.filter(
                policy_template__policy=policy,
                user=user,
                is_acknowledged=False,
                expired_at__isnull=True
            ).first()
            
            if existing_acknowledgment:
                return Response(
                    {'error': 'An active acknowledgment request already exists for this policy'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            acknowledgment = PolicyAcknowledgment.objects.create(**{
                'policy_template': policy_template,
                'user': user,
                'is_recurring': request.data.get('is_recurring', False),
                'is_user_initiated': request.data.get('is_user_initiated', False),
                'requested_at': timezone.now()
            })
            
            serializer = PolicyAcknowledgmentSerializer(acknowledgment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=True, methods=['put'])
    def acknowledge(self, request, pk=None):
        try:
            acknowledgment = self.get_object()
            
            if acknowledgment.is_acknowledged:
                return Response(
                    {'error': 'Policy is already acknowledged'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if acknowledgment.expired_at and acknowledgment.expired_at < timezone.now():
                return Response(
                    {'error': 'Policy acknowledgment request has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            acknowledgment.is_acknowledged = True
            acknowledgment.acknowledged_at = timezone.now()
            acknowledgment.save()
            
            serializer = self.get_serializer(acknowledgment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeptViewSet(viewsets.ModelViewSet):
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    
    def get_queryset(self):
        """
        Optionally filter by name using query parameter
        """
        queryset = Dept.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class DeptPolicyViewSet(viewsets.ModelViewSet):
    queryset = DeptPolicy.objects.all()
    serializer_class = DeptPolicySerializer
    
    def get_queryset(self):
        """
        Optionally filter by department or policy
        """
        queryset = DeptPolicy.objects.all()
        dept_id = self.request.query_params.get('dept_id', None)
        policy_id = self.request.query_params.get('policy_id', None)
        
        if dept_id is not None:
            queryset = queryset.filter(dept_id=dept_id)
        if policy_id is not None:
            queryset = queryset.filter(policy_id=policy_id)
        
        return queryset.select_related('dept', 'policy')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dept_policy = DeptPolicy.objects.create(
            dept_id=serializer.validated_data['dept_id'],
            policy_id=serializer.validated_data['policy_id']
        )
        
        # Fetch the complete object with related fields for response
        dept_policy = DeptPolicy.objects.select_related('dept', 'policy').get(id=dept_policy.id)
        response_serializer = self.get_serializer(dept_policy)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)