import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import Loader from '../components/Loader';
import './ProductPage.css';

export default function ProductPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [amount, setAmount] = useState(1);
  const navigate = useNavigate();
  const toast = useToast();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get(`/products/${productId}`);
        setProduct(data);
      } catch {
        toast.error('Товар не найден');
        navigate('/');
      } finally {
        setLoading(false);
      }
    })();
  }, [productId, navigate, toast]);

  const requireAuth = () => {
    if (!isAuthenticated) {
      toast.warning('Войдите в аккаунт для покупок');
      navigate('/login');
      return false;
    }
    return true;
  };

  const handleAddToCart = async () => {
    if (!requireAuth()) return;
    try {
      await api.post('/cart', { product_id: product.id, amount });
      toast.success(`${product.name} добавлен в корзину (${amount} шт.)`);
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleOrder = async () => {
    if (!requireAuth()) return;
    try {
      await api.post('/orders/', { product_id: product.id, amount });
      toast.success('Заказ создан!');
      navigate('/orders');
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <Loader size="lg" text="Загрузка товара..." />;
  if (!product) return null;

  return (
    <div className="product-page animate-fadeIn">
      <button className="btn btn-ghost" onClick={() => navigate(-1)} id="back-btn">
        ← Назад
      </button>

      <div className="product-detail-card glass-strong">
        <div className="product-detail-visual">
          <div className="product-detail-icon gradient-border">
            <span className="gradient-text">{product.name?.[0]?.toUpperCase()}</span>
          </div>
        </div>

        <div className="product-detail-info">
          <div className="product-detail-header">
            <h1 className="product-detail-name">{product.name}</h1>
            {product.category && (
              <span className="badge badge-violet">{product.category.name}</span>
            )}
          </div>

          {product.description && (
            <p className="product-detail-desc">{product.description}</p>
          )}

          <div className="product-detail-price">
            <span className="product-detail-price-value gradient-text">
              ₽{Number(product.price).toLocaleString('ru-RU')}
            </span>
            <span className={`product-stock ${product.now_amount > 0 ? 'in-stock' : 'out-of-stock'}`}>
              {product.now_amount > 0 ? `В наличии: ${product.now_amount} шт.` : 'Нет в наличии'}
            </span>
          </div>

          {product.now_amount > 0 && (
            <div className="product-detail-actions">
              <div className="amount-control">
                <button
                  className="btn btn-secondary btn-icon"
                  onClick={() => setAmount(Math.max(1, amount - 1))}
                  disabled={amount <= 1}
                >−</button>
                <span className="amount-display">{amount}</span>
                <button
                  className="btn btn-secondary btn-icon"
                  onClick={() => setAmount(Math.min(product.now_amount, amount + 1))}
                  disabled={amount >= product.now_amount}
                >+</button>
              </div>

              <button className="btn btn-primary btn-lg" onClick={handleAddToCart} id="add-cart-btn">
                В корзину
              </button>
              <button className="btn btn-secondary btn-lg" onClick={handleOrder} id="quick-order-btn">
                Купить сейчас
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
