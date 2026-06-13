from enum import Enum


class OrderStatus(str, Enum):
    created = "created"  # Создан
    processing = "processing"  # В обработке/собирается
    delivery = "delivery"  # В пути (доставляется)
    delivered = "delivered"  # Доставлен клиенту
    cancelled = "cancelled"  # Отменен (всегда нужен в магазине)


class UserRole(str, Enum):
    admin = "admin"  # can deactive user, but not create role admin
    user = "user"
    creator = "creator"  # can change role admin


class CreatorUserRole(str, Enum):
    admin = "admin"
    user = "user"
