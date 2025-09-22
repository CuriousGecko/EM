from functools import wraps

from access.api.exceptions import ObjectAccessDeniedError
from access.api.models import AccessRule
from django.http import JsonResponse
from rest_framework import permissions
from users.models import User


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только пользователям с ролью 'admin'."""
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and getattr(user, 'role', None) and
                    user.role.name == 'admin')


def check_access(
        allowed_methods: list[str],
        get_rules_for: str = None,
        require_auth: bool = True,
        require_admin: bool = False
):
    """Проверяет доступ к endpoint-у."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed_methods:
                return JsonResponse(
                    {'error': f'Метод {request.method} не разрешен.'},
                    status=405
                )

            user = request.user

            if require_auth and not getattr(user, 'is_active', False):
                return JsonResponse(
                    {'error': 'Требуется аутентификация.'},
                    status=401
                )

            if require_admin and not getattr(user, 'is_admin', False):
                return JsonResponse(
                    {'error': 'Требуются права администратора.'},
                    status=403
                )

            if get_rules_for:
                access_rules = get_access_rules(user, get_rules_for)
                if not access_rules:
                    return JsonResponse(
                        {'error': f'Для роли ({user.role}) не определены '
                                  f'правила доступа к ресурсу '
                                  f'({get_rules_for}).'},
                        status=403
                    )
                request.access_rules = access_rules
            else:
                request.access_rules = None

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def get_access_rules(user: User, element_name: str) -> AccessRule | None:
    """Вернет rule object для элемента или None."""
    try:
        return user.role.rules.get(element__name=element_name)
    except AccessRule.DoesNotExist:
        return None


def check_object_access(
        request_user: User,
        target_obj,
        access_rules: AccessRule,
        action: str
):
    """Проверит доступ к конкретному объекту."""
    if not access_rules:
        raise ObjectAccessDeniedError('Нет прав доступа.')

    if action == 'create':
        if not getattr(access_rules, 'can_create', False):
            raise ObjectAccessDeniedError('Нет прав на создание.')
        return

    action_field = f'can_{action}'
    can_all = getattr(access_rules, f'{action_field}_all', False)
    can_own = getattr(access_rules, f'{action_field}_own', False)

    if can_all or (can_own and is_owner(request_user, target_obj)):
        return
    raise ObjectAccessDeniedError('Доступ к объекту запрещен.')

def is_owner(request_user, target_obj):
    """Является ли пользователь владельцем объекта."""
    owner_id = getattr(target_obj, 'owner_id', None)
    if owner_id and owner_id == request_user.id:
        return True
    return False
