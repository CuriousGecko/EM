from access.api.models import AccessRule, BusinessElement
from rest_framework import serializers


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ['id', 'name']


class AccessRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)

    class Meta:
        model = AccessRule
        fields = [
            'id', 'role', 'role_name', 'element', 'element_name',
            'can_read_own', 'can_read_all', 'can_create', 'can_update_own',
            'can_update_all', 'can_delete_own', 'can_delete_all',
        ]
