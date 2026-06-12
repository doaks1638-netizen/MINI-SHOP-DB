import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import OrderCard from '../components/OrderCard';
import Pagination from '../components/Pagination';
import Loader from '../components/Loader';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const toast = useToast();
  const { refreshUser } = useAuth();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/users/me/orders?page=${page}`);
      
      const detailedOrders = await Promise.all(data.map(async (order) => {
        try {
          const product = await api.get(`/products/${order.product_id}`);
          return { ...order, product };
        } catch {
          return { ...order, product: null };
        }
      }));
      
      setOrders(detailedOrders);
    } catch {
      toast.error('Ошибка загрузки заказов');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleCancel = async (orderId) => {
    try {
      await api.delete(`/orders/me/${orderId}`);
      toast.success('Заказ отменён');
      await refreshUser();
      fetchOrders();
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <Loader size="lg" text="Загрузка заказов..." />;

  return (
    <div className="orders-page animate-fadeIn">
      <div className="page-header">
        <h1>
          <span className="gradient-text">Мои</span> заказы
        </h1>
        <p>{orders.length > 0 ? `Страница ${page}` : 'У вас пока нет заказов'}</p>
      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📦</div>
          <h3>Нет заказов</h3>
          <p>Ваши оформленные заказы появятся здесь</p>
        </div>
      ) : (
        <>
          <div className="stagger" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-md)' }}>
            {orders.map(order => (
              <OrderCard key={order.id} order={order} onCancel={handleCancel} />
            ))}
          </div>
          <Pagination page={page} onPageChange={setPage} hasMore={orders.length === 30} />
        </>
      )}
    </div>
  );
}
