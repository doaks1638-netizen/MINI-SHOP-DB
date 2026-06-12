import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';
import { HiOutlineTrash } from 'react-icons/hi';
import './AdminPages.css';

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const toast = useToast();

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/admin/users/?page=${page}`);
      setUsers(data);
    } catch {
      toast.error('Ошибка загрузки пользователей');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  if (loading) return <Loader size="lg" text="Загрузка пользователей..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> пользователями</h1>
      </div>

      <div className="admin-toolbar">
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
              <tr key={i}>
                <td><strong>{u.name}</strong></td>
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
