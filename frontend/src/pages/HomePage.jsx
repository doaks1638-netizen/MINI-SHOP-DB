import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import ProductCard from '../components/ProductCard';
import CategoryChip from '../components/CategoryChip';
import Pagination from '../components/Pagination';
import Loader from '../components/Loader';
import './HomePage.css';

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const toast = useToast();
  const { isAuthenticated } = useAuth();

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      let url = `/products/?page=${page}`;
      if (selectedCategory) url += `&category_id=${selectedCategory}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      const data = await api.get(url);
      setProducts(data);
    } catch (err) {
      toast.error('Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [page, selectedCategory, search, toast]);

  const fetchCategories = useCallback(async () => {
    try {
      const data = await api.get('/categories?page=1');
      setCategories(data);
    } catch {
      // Ignore
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleAddToCart = async (product) => {
    if (!isAuthenticated) {
      toast.warning('Войдите в аккаунт, чтобы добавить товар в корзину');
      navigate('/login');
      return;
    }
    try {
      await api.post('/cart', { product_id: product.id, amount: 1 });
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
      <div className="page-header">
        <h1>
          <span className="gradient-text">Каталог</span> товаров
        </h1>
        <p>Откройте для себя лучшие товары по доступным ценам</p>
      </div>

      <div className="home-filters">
        <div className="home-search">
          <input
            type="text"
            className="input"
            placeholder="Поиск товаров..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            id="product-search"
          />
        </div>

        {categories.length > 0 && (
          <div className="home-categories">
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
