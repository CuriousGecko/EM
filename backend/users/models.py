import uuid

import bcrypt
from access.api.models import AccessRole
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Менеджер объектов пользователей."""

    def create_user(
            self,
            email,
            password,
            last_name,
            first_name,
            patronymic='',
            role=None,
    ):
        if not email:
            raise ValueError('Email обязателен')
        if not password:
            raise ValueError('Пароль обязателен')

        email = self.normalize_email(email)

        if role is None:
            role, created = AccessRole.objects.get_or_create(name='user')

        elif isinstance(role, str):
            role, created = AccessRole.objects.get_or_create(name=role)

        elif not isinstance(role, AccessRole):
            raise ValueError(
                'Роль должна быть строкой, объектом AccessRole или None'
            )

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password,
        first_name,
        last_name,
    ):
        return self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin',
        )


class User(models.Model):
    """Модель пользователя."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(
        max_length=100,
        blank=True,
        default='',
    )
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    role = models.ForeignKey(
        'access.AccessRole',
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        db_table = 'auth_users'

    def set_password(self, raw_password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            raw_password.encode('utf-8'),
            salt,
        ).decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                raw_password.encode('utf-8'),
                self.password_hash.encode('utf-8'),
            )
        except (ValueError, AttributeError):
            return False

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts)

    @property
    def owner_id(self):
        return self.id

    @property
    def is_admin(self):
        return self.role.name == 'admin'

    def __str__(self):
        return (
            f'{self.full_name} '
            f'({self.email}) - {self.role.name}'
        )
