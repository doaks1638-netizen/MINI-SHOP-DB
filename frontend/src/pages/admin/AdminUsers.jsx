import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';

import './AdminPages.css';

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [roleFilter, setRoleFilter] = useState('');
  const toast = useToast();

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const query = { page };
      if (roleFilter) query.roles = [roleFilter];
      const data = await api.get('/admin/users/', query);
      setUsers(data);
    } catch {
      toast.error('Ошибка загрузки пользователей');
    } finally {
      setLoading(false);
    }
  }, [page, roleFilter, toast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchUsers]);

  if (loading) return <Loader size="lg" text="Загрузка пользователей..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> пользователями</h1>
      </div>

      <div className="admin-toolbar" style={{ flexDirection: 'row', alignItems: 'center', gap: 'var(--space-md)' }}>
        <select 
          className="input home-sort"
          value={roleFilter}
          onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
        >
          <option value="">Все роли</option>
          <option value="user">Пользователи</option>
          <option value="admin">Администраторы</option>
          <option value="creator">Создатели</option>
        </select>
        <span className="badge badge-green">{users.length} пользователей</span>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Имя</th>
              <th>Заказов</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={i} style={{ opacity: u.is_user_active === false ? 0.6 : 1 }}>
                <td>
                  <strong>{u.name}</strong>
                  {u.is_user_active === false && <span className="badge badge-red" style={{ marginLeft: 8 }}>Удалён</span>}
                </td>
                <td><span className="badge badge-violet">{u.orders_count}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Pagination page={page} onPageChange={setPage} hasMore={users.length === 30} />
    </div>
  );
}
