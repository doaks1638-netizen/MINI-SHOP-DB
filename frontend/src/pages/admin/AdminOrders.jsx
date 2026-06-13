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
  const [dateFilter, setDateFilter] = useState('new');
  const [statusFilter, setStatusFilter] = useState('');
  const toast = useToast();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const query = { page, date_filter: dateFilter };
      if (statusFilter) query.status_filter = statusFilter;
      const data = await api.get('/admin/orders/', query);
      setOrders(data);
    } catch {
      toast.error('Ошибка загрузки заказов');
    } finally {
      setLoading(false);
    }
  }, [page, dateFilter, statusFilter, toast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchOrders();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchOrders]);

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

      <div className="admin-toolbar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 'var(--space-sm)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-md)', width: '100%', maxWidth: '600px' }}>
          <select 
            className="input home-sort"
            value={dateFilter}
            onChange={(e) => { setDateFilter(e.target.value); setPage(1); }}
          >
            <option value="new">Сначала новые</option>
            <option value="old">Сначала старые</option>
          </select>
          <select 
            className="input home-sort"
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          >
            <option value="">Все статусы</option>
            <option value="created">Создан</option>
            <option value="processing">В обработке</option>
            <option value="delivery">Доставляется</option>
            <option value="delivered">Доставлен</option>
            <option value="cancelled">Отменен</option>
          </select>
        </div>
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
