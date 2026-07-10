import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import Pagination from '../components/Pagination';
import Loader from '../components/Loader';
import { HiOutlineTrash, HiOutlineMinus, HiOutlinePlus } from 'react-icons/hi';
import './CartPage.css';

export default function CartPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [orderingAll, setOrderingAll] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();
  const { refreshUser } = useAuth();

  const fetchCart = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get(`/cart/?page=${page}`);
      
      const detailedItems = await Promise.all(data.map(async (item) => {
        try {
          const product = await api.get(`/products/${item.product_id}`);
          return { ...item, product };
        } catch {
          return { ...item, product: null };
        }
      }));

      setItems(detailedItems);
    } catch {
      toast.error('Ошибка загрузки корзины');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleChangeAmount = async (productId, newAmount) => {
    try {
      await api.patch(`/cart/products/${productId}`, { new_amount: newAmount });
      setItems(prev => prev.map(i => i.product_id === productId ? { ...i, amount: newAmount } : i));
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleRemove = async (productId) => {
    try {
      await api.delete(`/cart/products/${productId}`);
      setItems(prev => prev.filter(i => i.product_id !== productId));
      toast.success('Товар удалён из корзины');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleOrderAll = async () => {
    setOrderingAll(true);
    try {
      await api.post('/orders/cart');
      toast.success('Все заказы из корзины оформлены!');
      await refreshUser();
      setItems([]);
      navigate('/orders');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setOrderingAll(false);
    }
  };

  const totalAmount = items.reduce((sum, item) => sum + (item.product ? item.product.price * item.amount : 0), 0);
  const hasOutOfStock = items.some(item => item.status === 'out_of_stock' || (item.product && item.product.now_amount < item.amount));
  const totalItemsCount = items.reduce((sum, item) => sum + item.amount, 0);

  if (loading) return <Loader size="lg" text="Загрузка корзины..." />;

  return (
    <div className="cart-page animate-fadeIn">
      <div className="page-header">
        <h1>Корзина</h1>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <h3>В корзине пока пусто</h3>
          <p>Загляните в каталог, чтобы выбрать товары</p>
          <button className="btn btn-primary" onClick={() => navigate('/')} style={{ marginTop: 24, padding: '12px 32px' }}>
            Перейти к покупкам
          </button>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items-section">
            <div className="cart-items stagger">
              {items.map(item => (
                <div key={item.product_id} className={`cart-item glass ${item.status === 'out_of_stock' ? 'out-of-stock-item' : ''}`} id={`cart-item-${item.product_id}`}>
                  
                  <div className="cart-item-visual">
                    {item.product?.image_url ? (
                      <img src={item.product.image_url} alt={item.product.name} />
                    ) : (
                      <div className="cart-item-placeholder">
                        {item.product?.name?.[0] || '?'}
                      </div>
                    )}
                  </div>

                  <div className="cart-item-details">
                    {item.product ? (
                      <>
                        <Link to={`/product/${item.product_id}`} className="cart-item-title">
                          {item.product.name}
                        </Link>
                        
                        {(item.status === 'out_of_stock' || item.product.now_amount < item.amount) && (
                          <div className="cart-item-error">
                            Недостаточно на складе
                          </div>
                        )}
                        
                        <div className="cart-item-bottom">
                           <div className="cart-item-amount-control">
                            <button
                              className="btn-icon"
                              onClick={() => handleChangeAmount(item.product_id, Math.max(1, item.amount - 1))}
                              disabled={item.amount <= 1}
                            >
                              <HiOutlineMinus size={14} />
                            </button>
                            <span className="cart-amount-value">{item.amount}</span>
                            <button
                              className="btn-icon"
                              onClick={() => handleChangeAmount(item.product_id, item.amount + 1)}
                              disabled={item.status === 'out_of_stock' || item.product.now_amount <= item.amount}
                            >
                              <HiOutlinePlus size={14} />
                            </button>
                          </div>
                          
                          <div className="cart-item-price-block">
                            <span className="cart-item-price">₽{Number(item.product.price).toLocaleString('ru-RU')}</span>
                            {item.amount > 1 && (
                              <span className="cart-item-price-total">
                                ₽{(item.product.price * item.amount).toLocaleString('ru-RU')}
                              </span>
                            )}
                          </div>
                        </div>
                      </>
                    ) : (
                      <span className="cart-item-title">Товар недоступен</span>
                    )}
                  </div>
                  
                  <button
                    className="cart-item-remove"
                    onClick={() => handleRemove(item.product_id)}
                    title="Удалить"
                    id={`remove-cart-${item.product_id}`}
                  >
                    <HiOutlineTrash size={20} />
                  </button>
                </div>
              ))}
            </div>
            {items.length > 0 && <Pagination page={page} onPageChange={setPage} hasMore={items.length === 30} />}
          </div>

          <div className="cart-sidebar">
            <div className="cart-summary glass-strong animate-slideInRight">
              <h2>Ваш заказ</h2>
              
              <div className="summary-details">
                <div className="summary-row">
                  <span>Товары ({totalItemsCount})</span>
                  <span>₽{totalAmount.toLocaleString('ru-RU')}</span>
                </div>
                <div className="summary-row">
                  <span>Скидка</span>
                  <span style={{ color: 'var(--accent-red)' }}>₽0</span>
                </div>
                <div className="summary-row">
                  <span>Доставка</span>
                  <span style={{ color: 'var(--accent-green)' }}>Бесплатно</span>
                </div>
              </div>

              <div className="summary-divider"></div>
              
              <div className="summary-total">
                <span>Итого</span>
                <span className="total-price">₽{totalAmount.toLocaleString('ru-RU')}</span>
              </div>
              
              {hasOutOfStock && (
                <div className="summary-warning">
                  Некоторые товары недоступны. Они не будут включены в заказ.
                </div>
              )}

              <button
                className="btn btn-primary btn-lg checkout-btn"
                onClick={handleOrderAll}
                disabled={orderingAll || items.length === 0}
                id="order-all-btn"
              >
                {orderingAll ? 'Оформление...' : 'Перейти к оформлению'}
              </button>
              
              <p className="checkout-terms">
                Нажимая на кнопку, вы соглашаетесь с Условиями обработки персональных данных.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

