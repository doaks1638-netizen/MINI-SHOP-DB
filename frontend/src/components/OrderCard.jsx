import './OrderCard.css';

const statusLabels = {
  created: 'Создан',
  processing: 'В обработке',
  delivery: 'Доставляется',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
};

const statusIcons = {
  created: '📋',
  processing: '⚙️',
  delivery: '🚚',
  delivered: '✅',
  cancelled: '❌',
};

export default function OrderCard({ order, onCancel, onStatusChange, showActions = true }) {
  const date = new Date(order.created_at).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="order-card card" id={`order-${order.id}`}>
      <div className="order-card-header">
        <div className="order-card-id">
          <span className="order-label">Заказ</span>
          <span className="order-id-text">#{order.id.slice(0, 8)}</span>
        </div>
        <span className={`badge status-${order.status}`}>
          {statusIcons[order.status]} {statusLabels[order.status] || order.status}
        </span>
      </div>

      <div className="order-card-body">
        {order.is_user_active === false && (
          <div className="order-detail" style={{ marginBottom: '8px' }}>
            <span className="badge badge-red">Пользователь удалён</span>
          </div>
        )}
        <div className="order-detail">
          <span className="order-detail-label">Количество</span>
          <span className="order-detail-value">{order.amount} шт.</span>
        </div>
        <div className="order-detail">
          <span className="order-detail-label">Дата</span>
          <span className="order-detail-value">{date}</span>
        </div>
        {order.product && (
          <div className="order-detail">
            <span className="order-detail-label">Товар</span>
            <span className="order-detail-value">{order.product.name}</span>
          </div>
        )}
      </div>

      {showActions && order.status !== 'cancelled' && order.status !== 'delivered' && (
        <div className="order-card-actions">
          {onCancel && (
            <button className="btn btn-danger btn-sm" onClick={() => onCancel(order.id)} id={`cancel-order-${order.id}`}>
              Отменить
            </button>
          )}
          {onStatusChange && (
            <select
              className="input order-status-select"
              value={order.status}
              onChange={(e) => onStatusChange(order.id, e.target.value)}
            >
              <option value="created">Создан</option>
              <option value="processing">В обработке</option>
              <option value="delivery">Доставляется</option>
              <option value="delivered">Доставлен</option>
              <option value="cancelled">Отменён</option>
            </select>
          )}
        </div>
      )}
    </div>
  );
}
