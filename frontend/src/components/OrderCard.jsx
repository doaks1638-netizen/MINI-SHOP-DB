import { Link } from 'react-router-dom';
import './OrderCard.css';

const statusLabels = {
  created: 'Создан',
  processing: 'В сборке',
  delivery: 'В пути',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
};

const statusIcons = {
  created: '📋',
  processing: '📦',
  delivery: '🚚',
  delivered: '✅',
  cancelled: '❌',
};

export default function OrderCard({ order, onCancel, onStatusChange, showActions = true }) {
  const date = new Date(order.created_at).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="order-card glass" id={`order-${order.id}`}>
      <div className="order-card-header">
        <div className="order-card-id">
          <span className="order-label">Заказ от {date}</span>
          <span className="order-id-text">#{order.id.slice(0, 8)}</span>
        </div>
        <span className={`badge status-${order.status} badge-outline`}>
          {statusIcons[order.status]} {statusLabels[order.status] || order.status}
        </span>
      </div>

      <div className="order-card-body">
        {order.is_user_active === false && (
          <div className="order-detail" style={{ marginBottom: '8px' }}>
            <span className="badge badge-red">Пользователь удалён</span>
          </div>
        )}
        
        {order.product ? (
          <div className="order-product-compact">
            <div className="order-product-visual">
              {order.product.image_url ? (
                <img src={order.product.image_url} alt={order.product.name} />
              ) : (
                <div className="order-product-placeholder">{order.product.name?.[0]}</div>
              )}
            </div>
            <div className="order-product-info">
              <Link to={`/product/${order.product.id}`} className="order-product-name">
                {order.product.name}
              </Link>
              <span className="order-product-meta">Количество: {order.amount} шт.</span>
              <span className="order-product-price">
                ₽{(order.product.price * order.amount).toLocaleString('ru-RU')}
              </span>
            </div>
          </div>
        ) : (
          <div className="order-detail">
            <span className="order-detail-label">Товар недоступен</span>
            <span className="order-detail-value">{order.amount} шт.</span>
          </div>
        )}
      </div>

      {showActions && order.status !== 'cancelled' && order.status !== 'delivered' && (
        <div className="order-card-actions">
          {onCancel && (
            <button className="btn btn-secondary btn-sm" onClick={() => onCancel(order.id)} id={`cancel-order-${order.id}`}>
              Отменить заказ
            </button>
          )}
          {onStatusChange && (
            <select
              className="input order-status-select"
              value={order.status}
              onChange={(e) => onStatusChange(order.id, e.target.value)}
            >
              <option value="created">Создан</option>
              <option value="processing">В сборке</option>
              <option value="delivery">В пути</option>
              <option value="delivered">Доставлен</option>
              <option value="cancelled">Отменён</option>
            </select>
          )}
        </div>
      )}
    </div>
  );
}

