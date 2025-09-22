from rest_framework import serializers
from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'last_name',
            'first_name',
            'patronymic',
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id',
            'last_name',
            'first_name',
            'patronymic',
            'full_name',
            'email',
            'is_active',
            'role',
        )
        read_only_fields = ('id', 'is_active', 'role')


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'last_name',
            'first_name',
            'patronymic',
            'email',
            'password',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
