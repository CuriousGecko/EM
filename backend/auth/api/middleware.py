from access.api.models import AccessRole, Session
from django.utils import timezone


class SessionAuthenticationMiddleware:
    """Middleware для установки пользователя в request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = self._get_user(request)
        return self.get_response(request)

    def _get_user(self, request):
        """Возвращает аутентифицированного пользователя или гостя."""
        session_id = request.COOKIES.get('sessionid')
        if session_id:
            try:
                session = Session.objects.select_related('user').get(
                    session_id=session_id,
                    is_valid=True,
                    expire_at__gt=timezone.now()
                )
                return session.user
            except Session.DoesNotExist:
                pass

        return self._create_guest_user()

    def _create_guest_user(self):
        """Создает гостевого пользователя."""
        guest_role, created = AccessRole.objects.get_or_create(
            name='guest',
        )

        return type('GuestUser', (), {
            'is_active': False,
            'role': guest_role,
            'id': None,
            'username': 'guest'
        })()
