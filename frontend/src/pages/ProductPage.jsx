import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { HiOutlineShoppingCart, HiOutlineLightningBolt } from 'react-icons/hi';
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
      await api.post('/cart/', { product_id: product.id, amount });
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
      <button className="btn btn-ghost product-page-back" onClick={() => navigate(-1)} id="back-btn">
        ← Назад в каталог
      </button>

      <div className="product-layout">
        {/* Left Side: Info & Image */}
        <div className="product-main">
          <div className="product-header">
            <h1 className="product-title">{product.name}</h1>
            {product.category && (
              <span className="badge badge-cyan">{product.category.name}</span>
            )}
          </div>

          <div className="product-gallery glass">
            {product.image_url ? (
              <img src={product.image_url} alt={product.name} className="product-image" />
            ) : (
              <div className="product-image-placeholder">
                <span>{product.name?.[0]?.toUpperCase()}</span>
              </div>
            )}
          </div>

          {product.description && (
            <div className="product-description-block glass">
              <h2>О товаре</h2>
              <p>{product.description}</p>
            </div>
          )}
        </div>

        {/* Right Side: Buy Pane */}
        <div className="product-sidebar">
          <div className="buy-pane glass-strong">
            <div className="buy-pane-price">
              <span className="price-value">₽{Number(product.price).toLocaleString('ru-RU')}</span>
            </div>

            <div className="buy-pane-stock">
              {product.now_amount > 0 ? (
                <span className="stock-ok">В наличии: {product.now_amount} шт.</span>
              ) : (
                <span className="stock-out">Нет в наличии</span>
              )}
            </div>

            {product.now_amount > 0 && (
              <>
                <div className="buy-pane-amount">
                  <span className="amount-label">Количество:</span>
                  <div className="amount-control">
                    <button
                      className="btn-icon"
                      onClick={() => setAmount(Math.max(1, amount - 1))}
                      disabled={amount <= 1}
                    >−</button>
                    <span className="amount-display">{amount}</span>
                    <button
                      className="btn-icon"
                      onClick={() => setAmount(Math.min(product.now_amount, amount + 1))}
                      disabled={amount >= product.now_amount}
                    >+</button>
                  </div>
                </div>

                <div className="buy-pane-actions">
                  <button className="btn btn-primary btn-lg w-full" onClick={handleAddToCart} id="add-cart-btn">
                    <HiOutlineShoppingCart size={22} />
                    В корзину
                  </button>
                  <button className="btn btn-secondary btn-lg w-full" onClick={handleOrder} id="quick-order-btn">
                    <HiOutlineLightningBolt size={22} />
                    Купить сейчас
                  </button>
                </div>
              </>
            )}
            
            <div className="buy-pane-delivery">
              <p>🚚 Доставка: завтра</p>
              <p>📦 Безопасная упаковка</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
