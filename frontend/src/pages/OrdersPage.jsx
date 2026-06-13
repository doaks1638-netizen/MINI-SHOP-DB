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
  const [dateFilter, setDateFilter] = useState('new');
  const [statusFilter, setStatusFilter] = useState('');
  const toast = useToast();
  const { refreshUser } = useAuth();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const query = { page, date_filter: dateFilter };
      if (statusFilter) query.status_filter = statusFilter;
      const data = await api.get('/orders/', query);
      
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
  }, [page, dateFilter, statusFilter, toast]);

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
        <p>Управляйте своими покупками и отслеживайте их статус</p>
      </div>

      <div className="home-search-row" style={{ marginBottom: 'var(--space-xl)' }}>
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
