from access.api.authentication import CustomSessionAuthentication
from access.api.models import AccessRule, BusinessElement
from access.api.permissions import IsAdmin
from access.api.serializers import (AccessRuleSerializer,
                                    BusinessElementSerializer)
from rest_framework import viewsets


class AdminViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet для административных API."""
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [IsAdmin]


class BusinessElementViewSet(AdminViewSet):
    """ViewSet для управления бизнес-элементами."""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer


class AccessRuleViewSet(AdminViewSet):
    """ViewSet для управления правилами доступа."""
    queryset = AccessRule.objects.select_related('role', 'element')
    serializer_class = AccessRuleSerializer
