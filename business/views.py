from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from permissions.utils import check_permission


# Mock данные для демонстрации
MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Товар 1', 'price': 100, 'owner_id': 1},
    {'id': 2, 'name': 'Товар 2', 'price': 200, 'owner_id': 2},
    {'id': 3, 'name': 'Товар 3', 'price': 300, 'owner_id': 1},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'quantity': 2, 'owner_id': 1},
    {'id': 2, 'product_id': 2, 'quantity': 1, 'owner_id': 2},
    {'id': 3, 'product_id': 3, 'quantity': 3, 'owner_id': 1},
]

MOCK_SHOPS = [
    {'id': 1, 'name': 'Магазин 1', 'address': 'Адрес 1', 'owner_id': 1},
    {'id': 2, 'name': 'Магазин 2', 'address': 'Адрес 2', 'owner_id': 2},
]


def get_product_owner(request, product_id):
    """Получает ID владельца продукта"""
    for product in MOCK_PRODUCTS:
        if product['id'] == product_id:
            return product['owner_id']
    return None


def get_order_owner(request, order_id):
    """Получает ID владельца заказа"""
    for order in MOCK_ORDERS:
        if order['id'] == order_id:
            return order['owner_id']
    return None


def get_order_owner_from_request(request, *args, **kwargs):
    """Получает ID владельца заказа из request"""
    order_id = kwargs.get('order_id')
    if order_id:
        return get_order_owner(request, order_id)
    return None


def get_shop_owner(request, shop_id):
    """Получает ID владельца магазина"""
    for shop in MOCK_SHOPS:
        if shop['id'] == shop_id:
            return shop['owner_id']
    return None


@api_view(['GET'])
@check_permission('products', 'read')
def list_products(request):
    """Список продуктов (только свои, если нет read_all)"""
    user_id = request.user.id
    
    # Если есть read_all, показываем все
    from permissions.utils import has_permission
    if has_permission(request.user, 'products', 'read_all'):
        return Response({'products': MOCK_PRODUCTS}, status=status.HTTP_200_OK)
    
    # Иначе только свои
    user_products = [p for p in MOCK_PRODUCTS if p['owner_id'] == user_id]
    return Response({'products': user_products}, status=status.HTTP_200_OK)


def get_product_owner_from_request(request, *args, **kwargs):
    """Получает ID владельца продукта из request"""
    product_id = kwargs.get('product_id')
    if product_id:
        return get_product_owner(request, product_id)
    return None


@api_view(['GET'])
@check_permission('products', 'read', check_owner=True, owner_getter=get_product_owner_from_request)
def get_product(request, product_id):
    """Получение продукта по ID"""
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'product': product}, status=status.HTTP_200_OK)


@api_view(['POST'])
@check_permission('products', 'create')
def create_product(request):
    """Создание нового продукта"""
    data = request.data.copy()
    data['owner_id'] = request.user.id
    data['id'] = len(MOCK_PRODUCTS) + 1
    MOCK_PRODUCTS.append(data)
    return Response({'product': data, 'message': 'Продукт создан'}, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@check_permission('products', 'update', check_owner=True, owner_getter=get_product_owner_from_request)
def update_product(request, product_id):
    """Обновление продукта"""
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    product.update(request.data)
    return Response({'product': product, 'message': 'Продукт обновлен'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@check_permission('products', 'delete', check_owner=True, owner_getter=get_product_owner_from_request)
def delete_product(request, product_id):
    """Удаление продукта"""
    global MOCK_PRODUCTS
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    MOCK_PRODUCTS = [p for p in MOCK_PRODUCTS if p['id'] != product_id]
    return Response({'message': 'Продукт удален'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@check_permission('orders', 'read')
def list_orders(request):
    """Список заказов"""
    user_id = request.user.id
    
    from permissions.utils import has_permission
    if has_permission(request.user, 'orders', 'read_all'):
        return Response({'orders': MOCK_ORDERS}, status=status.HTTP_200_OK)
    
    user_orders = [o for o in MOCK_ORDERS if o['owner_id'] == user_id]
    return Response({'orders': user_orders}, status=status.HTTP_200_OK)


@api_view(['GET'])
@check_permission('orders', 'read', check_owner=True, owner_getter=get_order_owner_from_request)
def get_order(request, order_id):
    """Получение заказа по ID"""
    order = next((o for o in MOCK_ORDERS if o['id'] == order_id), None)
    if not order:
        return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'order': order}, status=status.HTTP_200_OK)


@api_view(['GET'])
@check_permission('shops', 'read')
def list_shops(request):
    """Список магазинов"""
    user_id = request.user.id
    
    from permissions.utils import has_permission
    if has_permission(request.user, 'shops', 'read_all'):
        return Response({'shops': MOCK_SHOPS}, status=status.HTTP_200_OK)
    
    user_shops = [s for s in MOCK_SHOPS if s['owner_id'] == user_id]
    return Response({'shops': user_shops}, status=status.HTTP_200_OK)
