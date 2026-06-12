import { HiOutlineShoppingCart } from 'react-icons/hi';
import './ProductCard.css';

export default function ProductCard({ product, onAddToCart, onClick }) {
  const handleAdd = (e) => {
    e.stopPropagation();
    onAddToCart?.(product);
  };

  return (
    <div className="product-card card card-interactive gradient-border" onClick={() => onClick?.(product)} id={`product-${product.id}`}>
      <div className="product-card-visual" style={{ height: '200px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'var(--gradient-surface)', borderRadius: 'var(--radius-md) var(--radius-md) 0 0', margin: 'calc(-1 * var(--space-lg)) calc(-1 * var(--space-lg)) var(--space-md) calc(-1 * var(--space-lg))' }}>
        <div className="product-card-icon" style={{ fontSize: '4rem', fontWeight: 'bold', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          <span>{product.name?.[0]?.toUpperCase() || '?'}</span>
        </div>
      </div>
      <div className="product-card-body">
        <h3 className="product-card-name" style={{ fontSize: '1.25rem', marginBottom: '8px' }}>{product.name}</h3>
        {product.description && (
          <p className="product-card-desc" style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{product.description}</p>
        )}
        <div className="product-card-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="product-card-price">
            <span className="product-price-value" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>₽{Number(product.price).toLocaleString('ru-RU')}</span>
          </div>
          <div className="product-card-meta">
            <span className={`product-stock badge ${product.now_amount > 0 ? 'badge-green' : 'badge-red'}`}>
              {product.now_amount > 0 ? `${product.now_amount} шт.` : 'Нет в наличии'}
            </span>
          </div>
        </div>
      </div>
      {onAddToCart && product.now_amount > 0 && (
        <button className="product-card-add btn btn-primary w-full" onClick={handleAdd} id={`add-to-cart-${product.id}`} style={{ width: '100%', marginTop: '16px' }}>
          <HiOutlineShoppingCart size={18} />
          В корзину
        </button>
      )}
    </div>
  );
}
