import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import Pagination from '../components/Pagination';
import Loader from '../components/Loader';
import { HiOutlineTrash, HiOutlineShoppingCart, HiOutlineMinus, HiOutlinePlus } from 'react-icons/hi';
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
      const data = await api.get(`/cart/me?page=${page}`);
      
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
    const timer = setTimeout(() => {
      fetchCart();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchCart]);

  const handleChangeAmount = async (productId, newAmount) => {
    try {
      await api.patch(`/cart/me/products/${productId}`, { new_amount: newAmount });
      setItems(prev => prev.map(i => i.product_id === productId ? { ...i, amount: newAmount } : i));
      toast.success('Количество обновлено');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleRemove = async (productId) => {
    try {
      await api.delete(`/cart/me/products/${productId}`);
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

  if (loading) return <Loader size="lg" text="Загрузка корзины..." />;

  return (
    <div className="cart-page animate-fadeIn">
      <div className="page-header">
        <h1>
          <span className="gradient-text">Корзина</span>
        </h1>
        <p>{items.length > 0 ? `${items.length} товар(ов) в корзине` : 'Ваша корзина пуста'}</p>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🛒</div>
          <h3>Корзина пуста</h3>
          <p>Добавьте товары из каталога</p>
          <button className="btn btn-primary" onClick={() => navigate('/')} style={{ marginTop: 16 }}>
            Перейти в каталог
          </button>
        </div>
      ) : (
        <>
          <div className="cart-items stagger">
            {items.map(item => (
              <div key={item.product_id} className="cart-item card" id={`cart-item-${item.product_id}`}>
                <div className="cart-item-icon">
                  <HiOutlineShoppingCart size={24} />
                </div>
                <div className="cart-item-info" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  {item.product ? (
                    <>
                      <span className="cart-item-id" style={{ fontWeight: 600, fontSize: '1.1rem' }}>{item.product.name}</span>
                      <span className="cart-item-price" style={{ color: 'var(--text-secondary)' }}>₽{Number(item.product.price).toLocaleString('ru-RU')}</span>
                      {(item.product.now_amount === 0 || item.product.now_amount < item.amount) && (
                        <span className="cart-item-error" style={{ color: 'var(--accent-red)', fontWeight: 'bold', fontSize: '0.9rem', marginTop: '4px' }}>
                          ВНИМАНИЕ: Нет в наличии или недостаточно на складе!
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="cart-item-id" title={item.product_id}>
                      Товар #{item.product_id.slice(0, 8)} (Недоступен)
                    </span>
                  )}
                </div>
                <div className="cart-item-amount">
                  <button
                    className="btn btn-secondary btn-icon btn-sm"
                    onClick={() => handleChangeAmount(item.product_id, Math.max(1, item.amount - 1))}
                    disabled={item.amount <= 1}
                  >
                    <HiOutlineMinus size={14} />
                  </button>
                  <span className="cart-amount-value">{item.amount}</span>
                  <button
                    className="btn btn-secondary btn-icon btn-sm"
                    onClick={() => handleChangeAmount(item.product_id, item.amount + 1)}
                  >
                    <HiOutlinePlus size={14} />
                  </button>
                </div>
                <button
                  className="btn btn-danger btn-icon btn-sm"
                  onClick={() => handleRemove(item.product_id)}
                  id={`remove-cart-${item.product_id}`}
                >
                  <HiOutlineTrash size={16} />
                </button>
              </div>
            ))}
          </div>

          <div className="cart-footer">
            <button
              className="btn btn-primary btn-lg"
              onClick={handleOrderAll}
              disabled={orderingAll}
              id="order-all-btn"
            >
              {orderingAll ? 'Оформление...' : 'Оформить все заказы'}
            </button>
          </div>

          <Pagination page={page} onPageChange={setPage} hasMore={items.length === 30} />
        </>
      )}
    </div>
  );
}
