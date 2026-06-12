import { HiOutlineShoppingCart } from 'react-icons/hi';
import './ProductCard.css';

export default function ProductCard({ product, onAddToCart, onClick }) {
  const handleAdd = (e) => {
    e.stopPropagation();
    onAddToCart?.(product);
  };

  return (
    <div className="product-card card card-interactive gradient-border" onClick={() => onClick?.(product)} id={`product-${product.id}`}>
      <div className="product-card-visual">
        <div className="product-card-icon">
          <span>{product.name?.[0]?.toUpperCase() || '?'}</span>
        </div>
      </div>
      <div className="product-card-body">
        <h3 className="product-card-name">{product.name}</h3>
        {product.description && (
          <p className="product-card-desc">{product.description}</p>
        )}
        <div className="product-card-footer">
          <div className="product-card-price">
            <span className="product-price-value">₽{Number(product.price).toLocaleString('ru-RU')}</span>
          </div>
          <div className="product-card-meta">
            <span className={`product-stock ${product.now_amount > 0 ? 'in-stock' : 'out-of-stock'}`}>
              {product.now_amount > 0 ? `${product.now_amount} шт.` : 'Нет в наличии'}
            </span>
          </div>
        </div>
      </div>
      {onAddToCart && product.now_amount > 0 && (
        <button className="product-card-add btn btn-primary btn-sm" onClick={handleAdd} id={`add-to-cart-${product.id}`}>
          <HiOutlineShoppingCart size={16} />
          В корзину
        </button>
      )}
    </div>
  );
}
