import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';
import './AdminPages.css';

export default function AdminCarts() {
  const [carts, setCarts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const toast = useToast();

  const fetchCarts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/admin/cart/?page=${page}`);
      setCarts(data);
    } catch {
      toast.error('Ошибка загрузки корзин');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => { fetchCarts(); }, [fetchCarts]);

  if (loading) return <Loader size="lg" text="Загрузка корзин..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Корзины</span> пользователей</h1>
      </div>

      <div className="admin-toolbar">
        <span className="badge badge-pink">{carts.length} корзин</span>
      </div>

      {carts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <h3>Нет активных корзин</h3>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Товаров</th>
                <th>Всего единиц</th>
              </tr>
            </thead>
            <tbody>
              {carts.map((c, i) => (
                <tr key={i}>
                  <td><code style={{ color: 'var(--text-muted)', fontSize: 'var(--font-xs)' }}>{c.user_id?.slice(0, 12)}...</code></td>
                  <td><span className="badge badge-violet">{c.total_products}</span></td>
                  <td><span className="badge badge-cyan">{c.total_items}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} onPageChange={setPage} hasMore={carts.length === 30} />
    </div>
  );
}
