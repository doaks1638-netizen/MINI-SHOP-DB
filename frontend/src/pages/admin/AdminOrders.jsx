import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import OrderCard from '../../components/OrderCard';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';
import './AdminPages.css';

export default function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const toast = useToast();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/admin/orders/?page=${page}`);
      setOrders(data);
    } catch {
      toast.error('Ошибка загрузки заказов');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await api.patch(`/admin/orders/${orderId}`, { status: newStatus });
      toast.success('Статус обновлён');
      fetchOrders();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleCancel = async (orderId) => {
    try {
      await api.delete(`/admin/orders/${orderId}`);
      toast.success('Заказ отменён');
      fetchOrders();
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <Loader size="lg" text="Загрузка заказов..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> заказами</h1>
      </div>

      <div className="admin-toolbar">
        <span className="badge badge-amber">{orders.length} заказов</span>
      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📦</div>
          <h3>Нет активных заказов</h3>
        </div>
      ) : (
        <div className="stagger" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {orders.map(order => (
            <OrderCard
              key={order.id}
              order={order}
              onCancel={handleCancel}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}

      <Pagination page={page} onPageChange={setPage} hasMore={orders.length === 30} />
    </div>
  );
}
