from enum import Enum


class OrderStatus(str, Enum):
    created = "created"  # Создан
    processing = "processing"  # В обработке/собирается
    delivery = "delivery"  # В пути (доставляется)
    delivered = "delivered"  # Доставлен клиенту
    cancelled = "cancelled"  # Отменен (всегда нужен в магазине)
