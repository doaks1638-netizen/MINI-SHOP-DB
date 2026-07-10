import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import ProductCard from '../components/ProductCard';
import CategoryChip from '../components/CategoryChip';
import Pagination from '../components/Pagination';
import './HomePage.css';

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [priceFilter, setPriceFilter] = useState('');
  const navigate = useNavigate();
  const toast = useToast();
  const { isAuthenticated } = useAuth();

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const query = { page };
      if (selectedCategory) query.category_id = selectedCategory;
      if (search) query.search = search;
      if (priceFilter) query.price_filter = priceFilter;
      const data = await api.get('/products/', query);
      setProducts(data);
    } catch {
      toast.error('Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [page, selectedCategory, search, priceFilter, toast]);

  const fetchCategories = useCallback(async () => {
    try {
      const data = await api.get('/categories/', { page: 1 });
      setCategories(data);
    } catch {
      // Ignore
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCategories();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchCategories]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProducts();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchProducts]);

  const handleAddToCart = async (product) => {
    if (!isAuthenticated) {
      toast.warning('Войдите в аккаунт, чтобы добавить товар в корзину');
      navigate('/login');
      return;
    }
    try {
      await api.post('/cart/', { product_id: product.id, amount: 1 });
      toast.success(`${product.name} добавлен в корзину`);
    } catch (err) {
      toast.error(err.message || 'Ошибка добавления в корзину');
    }
  };

  const handleCategoryFilter = (cat) => {
    setSelectedCategory(prev => prev === cat.id ? null : cat.id);
    setPage(1);
  };

  return (
    <div className="home-page animate-fadeIn">
      <div className="home-filters-bar">
        {categories.length > 0 && (
          <div className="home-categories-scroll">
            <CategoryChip
              key="all"
              category={{ id: null, name: 'Все товары' }}
              isActive={selectedCategory === null}
              onClick={() => { setSelectedCategory(null); setPage(1); }}
            />
            {categories.map(cat => (
              <CategoryChip
                key={cat.id}
                category={cat}
                isActive={selectedCategory === cat.id}
                onClick={handleCategoryFilter}
              />
            ))}
          </div>
        )}

        <div className="home-controls">
          <input
            type="text"
            className="input home-search"
            placeholder="Искать в категории..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
          <select 
            className="input home-sort"
            value={priceFilter}
            onChange={(e) => { setPriceFilter(e.target.value); setPage(1); }}
          >
            <option value="">По популярности</option>
            <option value="cheaper">Сначала дешевые</option>
            <option value="more_expensive">Сначала дорогие</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="page-grid">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <div key={i} className="skeleton" style={{ height: '320px', borderRadius: 'var(--radius-lg)' }} />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛍️</div>
          <h3>Товары не найдены</h3>
          <p>Попробуйте изменить фильтры или поисковый запрос</p>
        </div>
      ) : (
        <>
          <div className="page-grid stagger">
            {products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                onClick={(p) => navigate(`/product/${p.id}`)}
              />
            ))}
          </div>
          <Pagination
            page={page}
            onPageChange={setPage}
            hasMore={products.length === 30}
          />
        </>
      )}
    </div>
  );
}
