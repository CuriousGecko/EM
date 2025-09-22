from access.api.models import Session
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomSessionAuthentication(BaseAuthentication):
    """Аутентификация по sessionid для DRF."""

    def authenticate(self, request):
        session_id = request.COOKIES.get('sessionid')
        if not session_id:
            return None

        try:
            session = Session.objects.select_related('user').get(
                session_id=session_id,
                is_valid=True,
                expire_at__gt=timezone.now()
            )
            return session.user, None
        except Session.DoesNotExist:
            raise AuthenticationFailed(
                'Недействительная или просроченная сессия.'
            )
