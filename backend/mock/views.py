from access.api.permissions import check_access
from django.http import JsonResponse


@check_access(
    allowed_methods=['GET'],
    require_auth=False
)
def get_products(request):
    """
    Mock API для получения списка товаров.
    Публичный endpoint - не требует аутентификации.
    """
    mock_products = [
        {
            'id': 1,
            'name': 'Ноутбук Lenovo Legion 5 2025',
            'price': 129999,
            'category': 'Электроника'
        },
        {
            'id': 2,
            'name': 'Смартфон iPhone 15 Pro',
            'price': 89999,
            'category': 'Электроника'
        },
        {
            'id': 3,
            'name': 'Наушники ATH-M50x',
            'price': 29999,
            'category': 'Аксессуары'
        }
    ]

    return JsonResponse({'products': mock_products})


@check_access(
    allowed_methods=['GET'],
    get_rules_for='order',
    require_auth=True
)
def get_orders(request):
    """
    Mock API для получения заказов.
    Требует аутентификацию и права на чтение заказов (своих или любых).
    """
    mock_orders = [
        {
            'id': 101,
            'owner_id': str(request.user.id),
            'status': 'delivered',
            'items': [
                {'product_id': 1, 'quantity': 1, 'price': 129999},
                {'product_id': 3, 'quantity': 1, 'price': 29999}
            ]
        },
        {
            'id': 102,
            'owner_id': 'dae3bbff-7566-4b87-89b4-e0075cebfd8f',
            'status': 'processing',
            'items': [
                {'product_id': 2, 'quantity': 1, 'price': 89999}
            ]
        }
    ]

    if request.access_rules.can_read_all:
        return JsonResponse(mock_orders, safe=False)

    if request.access_rules.can_read_own:
        user_orders = [
            order for order in mock_orders if
            order['owner_id'] == str(request.user.id)
        ]
        return JsonResponse(user_orders, safe=False)

    return JsonResponse(
        {'error': 'Нет доступа к заказам.'},
        status=403
    )
