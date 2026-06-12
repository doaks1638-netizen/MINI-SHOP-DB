import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Modal from '../../components/Modal';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';
import { HiOutlinePlus, HiOutlinePencil, HiOutlineTrash } from 'react-icons/hi';
import './AdminPages.css';

export default function AdminCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCat, setEditingCat] = useState(null);
  const [name, setName] = useState('');
  const toast = useToast();

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/categories?page=${page}`);
      setCategories(data);
    } catch {
      toast.error('Ошибка загрузки категорий');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCategories();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchCategories]);

  const openCreate = () => { setEditingCat(null); setName(''); setModalOpen(true); };
  const openEdit = (cat) => { setEditingCat(cat); setName(cat.name); setModalOpen(true); };

  const handleSubmit = async () => {
    try {
      if (editingCat) {
        await api.patch(`/admin/categories/${editingCat.id}`, { name });
        toast.success('Категория обновлена');
      } else {
        await api.post('/admin/categories/', { name });
        toast.success('Категория создана');
      }
      setModalOpen(false);
      fetchCategories();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить категорию? Все товары в ней будут деактивированы.')) return;
    try {
      await api.delete(`/admin/categories/${id}`);
      toast.success('Категория удалена');
      fetchCategories();
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <Loader size="lg" text="Загрузка категорий..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> категориями</h1>
      </div>

      <div className="admin-toolbar">
        <span className="badge badge-cyan">{categories.length} категорий</span>
        <button className="btn btn-primary" onClick={openCreate} id="create-category-btn">
          <HiOutlinePlus size={18} /> Добавить категорию
        </button>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(c => (
              <tr key={c.id}>
                <td><code style={{ color: 'var(--text-muted)', fontSize: 'var(--font-xs)' }}>{c.id.slice(0, 8)}</code></td>
                <td><strong>{c.name}</strong></td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(c)}><HiOutlinePencil size={16} /></button>
                    <button className="btn btn-danger btn-icon btn-sm" onClick={() => handleDelete(c.id)}><HiOutlineTrash size={16} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Pagination page={page} onPageChange={setPage} hasMore={categories.length === 30} />

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingCat ? 'Редактировать категорию' : 'Новая категория'} size="sm">
        <div className="admin-form">
          <div className="input-group">
            <label className="input-label">Название категории</label>
            <input className="input" value={name} onChange={e => setName(e.target.value)} placeholder="Введите название" maxLength={50} />
          </div>
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={() => setModalOpen(false)}>Отмена</button>
            <button className="btn btn-primary" onClick={handleSubmit}>{editingCat ? 'Сохранить' : 'Создать'}</button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
