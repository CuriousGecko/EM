import uuid

from django.db import models
from django.utils import timezone


class AccessRole(models.Model):
    """Роли пользователей."""

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Объекты/ресурсы приложения."""

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """Правила доступа."""

    role = models.ForeignKey(
        AccessRole,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name='rules'
    )

    can_read_own = models.BooleanField(default=False)
    can_read_all = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update_own = models.BooleanField(default=False)
    can_update_all = models.BooleanField(default=False)
    can_delete_own = models.BooleanField(default=False)
    can_delete_all = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')

    def __str__(self):
        return f'{self.role} → {self.element}'


class Session(models.Model):
    """Сессия пользователя (cookie-based)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
    )
    session_id = models.CharField(
        max_length=128,
        unique=True,
    )
    expire_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sessions'

    def __str__(self):
        return f'Session {self.session_id} for {self.user}'

    @classmethod
    def create_for_user(cls, user, hours_valid: int = 24):
        session_id = cls.generate_session_id()
        expire_at = timezone.now() + timezone.timedelta(hours=hours_valid)

        return cls.objects.create(
            user=user,
            session_id=session_id,
            expire_at=expire_at
        )

    @staticmethod
    def generate_session_id() -> str:
        """Создаст уникальный session_id."""
        return str(uuid.uuid4())

    def invalidate(self):
        """Делает сессию недействительной (logout)."""
        self.is_valid = False
        self.save()

    @property
    def is_expired(self) -> bool:
        """Проверка, истекла ли сессия."""
        return not self.is_valid or self.expire_at <= timezone.now()
