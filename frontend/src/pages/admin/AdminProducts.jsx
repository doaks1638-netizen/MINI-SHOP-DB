import { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Modal from '../../components/Modal';
import Pagination from '../../components/Pagination';
import Loader from '../../components/Loader';
import { HiOutlinePlus, HiOutlinePencil, HiOutlineTrash } from 'react-icons/hi';
import './AdminPages.css';

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form, setForm] = useState({ category_id: '', name: '', description: '', price: '', now_amount: '' });
  const toast = useToast();

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/products/?page=${page}`);
      setProducts(data);
    } catch {
      toast.error('Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  const fetchCategories = useCallback(async () => {
    try {
      const data = await api.get('/categories?page=1');
      setCategories(data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);
  useEffect(() => { fetchCategories(); }, [fetchCategories]);

  const openCreate = () => {
    setEditingProduct(null);
    setForm({ category_id: categories[0]?.id || '', name: '', description: '', price: '', now_amount: '' });
    setModalOpen(true);
  };

  const openEdit = (product) => {
    setEditingProduct(product);
    setForm({
      category_id: product.category_id,
      name: product.name,
      description: product.description || '',
      price: product.price,
      now_amount: product.now_amount,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const body = {
        ...form,
        price: parseFloat(form.price),
        now_amount: parseInt(form.now_amount),
        description: form.description || null,
      };

      if (editingProduct) {
        await api.patch(`/admin/products/${editingProduct.id}`, body);
        toast.success('Товар обновлён');
      } else {
        await api.post('/admin/products/', body);
        toast.success('Товар создан');
      }
      setModalOpen(false);
      fetchProducts();
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить товар?')) return;
    try {
      await api.delete(`/admin/products/${id}`);
      toast.success('Товар удалён');
      fetchProducts();
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <Loader size="lg" text="Загрузка товаров..." />;

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> товарами</h1>
      </div>

      <div className="admin-toolbar">
        <span className="badge badge-violet">{products.length} товаров</span>
        <button className="btn btn-primary" onClick={openCreate} id="create-product-btn">
          <HiOutlinePlus size={18} /> Добавить товар
        </button>
      </div>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Описание</th>
              <th>Цена</th>
              <th>Кол-во</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id}>
                <td><strong>{p.name}</strong></td>
                <td style={{ color: 'var(--text-muted)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.description || '—'}</td>
                <td><span className="gradient-text" style={{ fontWeight: 600 }}>₽{Number(p.price).toLocaleString('ru-RU')}</span></td>
                <td><span className={p.now_amount > 0 ? '' : 'out-of-stock'}>{p.now_amount}</span></td>
                <td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(p)}><HiOutlinePencil size={16} /></button>
                    <button className="btn btn-danger btn-icon btn-sm" onClick={() => handleDelete(p.id)}><HiOutlineTrash size={16} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Pagination page={page} onPageChange={setPage} hasMore={products.length === 30} />

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingProduct ? 'Редактировать товар' : 'Новый товар'}>
        <div className="admin-form">
          <div className="input-group">
            <label className="input-label">Категория</label>
            <select className="input" value={form.category_id} onChange={e => setForm({ ...form, category_id: e.target.value })}>
              <option value="">Выберите категорию</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Название</label>
            <input className="input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Название товара" />
          </div>
          <div className="input-group">
            <label className="input-label">Описание</label>
            <input className="input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Описание (опционально)" />
          </div>
          <div className="admin-form-row">
            <div className="input-group">
              <label className="input-label">Цена (₽)</label>
              <input className="input" type="number" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} placeholder="0.00" min="0" step="0.01" />
            </div>
            <div className="input-group">
              <label className="input-label">Количество</label>
              <input className="input" type="number" value={form.now_amount} onChange={e => setForm({ ...form, now_amount: e.target.value })} placeholder="0" min="0" />
            </div>
          </div>
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={() => setModalOpen(false)}>Отмена</button>
            <button className="btn btn-primary" onClick={handleSubmit}>{editingProduct ? 'Сохранить' : 'Создать'}</button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
