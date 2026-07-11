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
  const [activeFilter, setActiveFilter] = useState('all');
  const [priceFilter, setPriceFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form, setForm] = useState({ category_id: '', name: '', description: '', price: '', now_amount: '', is_active: true, picture_file: null });
  const [fieldErrors, setFieldErrors] = useState({});
  const toast = useToast();

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const query = { page };
      if (activeFilter) query.active_filter = activeFilter;
      if (priceFilter) query.price_filter = priceFilter;
      if (search) query.search = search;
      if (selectedCategory) query.category_id = selectedCategory;
      const data = await api.get('/admin/products/', query);
      setProducts(data);
    } catch {
      toast.error('Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [page, activeFilter, priceFilter, search, selectedCategory, toast]);

  const fetchCategories = useCallback(async () => {
    try {
      const data = await api.get('/admin/categories/', { active_filter: 'all', page: 1 });
      setCategories(data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProducts();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchProducts]);
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCategories();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchCategories]);

  const openCreate = () => {
    setEditingProduct(null);
    setForm({ category_id: categories[0]?.id || '', name: '', description: '', price: '', now_amount: '', is_active: true, picture_file: null });
    setFieldErrors({});
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
      is_active: product.is_active ?? true,
      picture_file: null,
    });
    setFieldErrors({});
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const payload = new FormData();
      if (form.category_id) payload.append('category_id', form.category_id);
      payload.append('name', form.name);
      if (form.description) payload.append('description', form.description);
      if (form.price !== '') payload.append('price', form.price);
      if (form.now_amount !== '') payload.append('now_amount', form.now_amount);
      payload.append('is_active', form.is_active);
      if (form.picture_file) {
        payload.append('picture_file', form.picture_file);
      }

      if (editingProduct) {
        await api.patch(`/admin/products/${editingProduct.id}`, payload);
        toast.success('Товар обновлён');
      } else {
        await api.post('/admin/products/', payload);
        toast.success('Товар создан');
      }
      setModalOpen(false);
      fetchProducts();
    } catch (err) {
      if (err.name === 'ApiError' && Object.keys(err.fields).length > 0) {
        setFieldErrors(err.fields);
        toast.error('Проверьте правильность заполнения полей');
      } else {
        toast.error(err.message);
      }
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

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1><span className="gradient-text">Управление</span> товарами</h1>
      </div>

      <div className="admin-toolbar">
        <button className="btn btn-primary" onClick={openCreate} id="create-product-btn">
          <HiOutlinePlus size={18} /> Добавить товар
        </button>
      </div>

      <div className="admin-filters-row">
        <input
          type="text"
          className="input admin-search-input"
          placeholder="Поиск товаров..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select 
          className="input admin-sort-select"
          value={selectedCategory}
          onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
        >
          <option value="">Все категории</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select 
          className="input admin-sort-select"
          value={activeFilter}
          onChange={(e) => { setActiveFilter(e.target.value); setPage(1); }}
        >
          <option value="all">Все статусы</option>
          <option value="active">Только активные</option>
          <option value="inactive">Только удаленные</option>
        </select>
        <select 
          className="input admin-sort-select"
          value={priceFilter}
          onChange={(e) => { setPriceFilter(e.target.value); setPage(1); }}
        >
          <option value="">По умолчанию</option>
          <option value="cheaper">Сначала дешевые</option>
          <option value="more_expensive">Сначала дорогие</option>
        </select>
      </div>

      {loading ? (
        <Loader size="lg" text="Загрузка товаров..." />
      ) : products.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛍️</div>
          <h3>Товары не найдены</h3>
          <p>Попробуйте изменить фильтры или поисковый запрос</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Изображение</th>
                  <th>Описание</th>
                  <th>Цена</th>
                  <th>Кол-во</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id} style={{ opacity: p.is_active === false ? 0.6 : 1 }}>
                    <td>
                      <strong>{p.name}</strong>
                      {p.is_active === false && <span className="badge badge-red" style={{ marginLeft: 8 }}>Удалён</span>}
                    </td>
                    <td>
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.name} style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 4 }} />
                      ) : (
                        <div style={{ width: 40, height: 40, background: '#eee', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>-</div>
                      )}
                    </td>
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
        </>
      )}

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingProduct ? 'Редактировать товар' : 'Новый товар'}>
        <div className="admin-form">
          <div className="input-group">
            <label className="input-label">Категория</label>
            <select className={`input ${fieldErrors.category_id ? 'input-error' : ''}`} value={form.category_id} onChange={e => { setForm({ ...form, category_id: e.target.value }); setFieldErrors({ ...fieldErrors, category_id: undefined }); }}>
              <option value="">Выберите категорию</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            {fieldErrors.category_id && <span className="field-error">{fieldErrors.category_id}</span>}
          </div>
          <div className="input-group">
            <label className="input-label">Название</label>
            <input className={`input ${fieldErrors.name ? 'input-error' : ''}`} value={form.name} onChange={e => { setForm({ ...form, name: e.target.value }); setFieldErrors({ ...fieldErrors, name: undefined }); }} placeholder="Название товара" />
            {fieldErrors.name && <span className="field-error">{fieldErrors.name}</span>}
          </div>
          <div className="input-group">
            <label className="input-label">Описание</label>
            <input className={`input ${fieldErrors.description ? 'input-error' : ''}`} value={form.description} onChange={e => { setForm({ ...form, description: e.target.value }); setFieldErrors({ ...fieldErrors, description: undefined }); }} placeholder="Описание (опционально)" />
            {fieldErrors.description && <span className="field-error">{fieldErrors.description}</span>}
          </div>
          <div className="admin-form-row">
            <div className="input-group">
              <label className="input-label">Цена (₽)</label>
              <input className={`input ${fieldErrors.price ? 'input-error' : ''}`} type="number" value={form.price} onChange={e => { setForm({ ...form, price: e.target.value }); setFieldErrors({ ...fieldErrors, price: undefined }); }} placeholder="0.00" min="0" step="0.01" />
              {fieldErrors.price && <span className="field-error">{fieldErrors.price}</span>}
            </div>
            <div className="input-group">
              <label className="input-label">Количество</label>
              <input className={`input ${fieldErrors.now_amount ? 'input-error' : ''}`} type="number" value={form.now_amount} onChange={e => { setForm({ ...form, now_amount: e.target.value }); setFieldErrors({ ...fieldErrors, now_amount: undefined }); }} placeholder="0" min="0" />
              {fieldErrors.now_amount && <span className="field-error">{fieldErrors.now_amount}</span>}
            </div>
          </div>
          <div className="input-group" style={{ marginTop: '1rem' }}>
            <label className="input-label">Изображение товара</label>
            <input 
              type="file" 
              className={`input ${fieldErrors.picture_file ? 'input-error' : ''}`} 
              accept="image/png, image/jpeg, image/webp" 
              onChange={e => { setForm({ ...form, picture_file: e.target.files[0] }); setFieldErrors({ ...fieldErrors, picture_file: undefined }); }} 
            />
            {fieldErrors.picture_file && <span className="field-error">{fieldErrors.picture_file}</span>}
            {editingProduct?.image_url && !form.picture_file && (
              <div style={{ marginTop: '8px' }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Текущее изображение:</p>
                <img src={editingProduct.image_url} alt="Current" style={{ width: 100, height: 100, objectFit: 'cover', borderRadius: 8 }} />
              </div>
            )}
          </div>
          <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px', marginTop: '1rem' }}>
            <input type="checkbox" id="is_active_checkbox" checked={form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} />
            <label htmlFor="is_active_checkbox" className="input-label" style={{ marginBottom: 0, cursor: 'pointer' }}>Товар активен (виден покупателям)</label>
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
