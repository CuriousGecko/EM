import uuid

from access.api.constants import Action
from access.api.models import AccessRule
from access.api.permissions import check_access, check_object_access
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from users.api.serializers import (UserRegisterSerializer, UserSerializer,
                                   UserUpdateSerializer)
from users.models import User
from utils.utils import parse_json_body


@csrf_exempt
@check_access(
    allowed_methods=['POST'],
    get_rules_for='user',
    require_auth=False
)
def register_user(
        request: HttpRequest,
        access_rules: AccessRule | None
) -> JsonResponse:
    """
    Регистрация нового пользователя в системе.

    Публичный endpoint, но требует права can_create для роли.
    Если регистрация отключена (can_create=False), возвращает 403.

    Args:
        request: HTTP запрос с данными регистрации
        access_rules: Правила доступа для ресурса 'user', полученные из роли

    Returns:
        JsonResponse:
            - 201: Успешная регистрация с данными пользователя
            - 400: Ошибки валидации данных
            - 403: Регистрация отключена (нет прав can_create)

    Example:
        POST /api/register/
        {
            "email": "user@example.com",
            "password": "supersecurepassword123",
            "password_confirm": "supersecurepassword123",
            "first_name": "Иван",
            "last_name": "Иванов"
        }
    """
    if not access_rules.can_create:
        return JsonResponse(
            {'errors': 'Регистрация в данный момент недоступна.'},
            status=403
        )

    payload = parse_json_body(request)
    serializer = UserRegisterSerializer(data=payload)

    if serializer.is_valid():
        user = serializer.save()
        return JsonResponse(
            UserSerializer(user).data,
            status=201
        )
    else:
        return JsonResponse(
            {'errors': serializer.errors},
            status=400
        )


@csrf_exempt
@check_access(
    allowed_methods=['GET'],
    get_rules_for='user',
)
def get_user_list(
        request: HttpRequest,
        access_rules: AccessRule | None
) -> JsonResponse:
    """Выдаст список всех пользователей или вернет текущего."""
    if access_rules.can_read_all:
        users = User.objects.filter(is_active=True)
        data = UserSerializer(users, many=True).data
        return JsonResponse({'users': data})
    else:
        data = UserSerializer(request.user).data
        return JsonResponse({'users': [data]})


@csrf_exempt
@check_access(
    allowed_methods=['GET'],
    get_rules_for='user',
)
def get_user_detail(
        request: HttpRequest,
        user_id: uuid.UUID,
        access_rules: AccessRule | None
) -> JsonResponse:
    """Выдаст информацию о пользователе."""
    user_to_read = get_object_or_404(User, id=user_id, is_active=True)
    check_object_access(request.user, user_to_read, access_rules, Action.READ)
    data = UserSerializer(user_to_read).data
    return JsonResponse({'user': data})


@csrf_exempt
@check_access(
    allowed_methods=['PUT'],
    get_rules_for='user',
)
def update_user(
        request: HttpRequest,
        user_id: uuid.UUID,
        access_rules: AccessRule | None
) -> JsonResponse:
    """Обновит информацию о пользователе."""
    user_to_update = get_object_or_404(User, id=user_id, is_active=True)
    check_object_access(
        request.user, user_to_update, access_rules, Action.UPDATE
    )

    payload = parse_json_body(request)

    serializer = UserUpdateSerializer(
        user_to_update,
        data=payload,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'user': serializer.data})
    else:
        return JsonResponse(
            {'errors': serializer.errors},
            status=400
        )


@csrf_exempt
@check_access(
    allowed_methods=['DELETE'],
    get_rules_for='user',
)
def delete_user(
        request: HttpRequest,
        user_id: uuid.UUID,
        access_rules: AccessRule | None
) -> JsonResponse:
    """
    Удалит пользователя (мягкое удаление).

    Проверит права доступа перед выполнением операции:
    - can_delete_all: разрешает удаление любого пользователя
    - can_delete_own: разрешает удаление только своих объектов

    Args:
        request: HTTP запрос
        user_id: UUID пользователя для удаления
        access_rules: Правила доступа для ресурса 'user'

    Returns:
        JsonResponse: Сообщение об успешном удалении (201) или ошибка

    Raises:
        Http404: Если пользователь не найден
        ObjectAccessDeniedError: Нет прав на удаление (преобразуется в 403)
    """
    user_to_delete = get_object_or_404(User, id=user_id, is_active=True)
    check_object_access(
        request.user, user_to_delete, access_rules, Action.DELETE
    )
    user_to_delete.soft_delete()
    return JsonResponse(
        {'message': 'Пользователь удалён.'}
    )
