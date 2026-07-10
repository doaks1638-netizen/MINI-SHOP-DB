import { HiOutlineShoppingCart } from 'react-icons/hi';
import './ProductCard.css';

export default function ProductCard({ product, onAddToCart, onClick }) {
  const handleAdd = (e) => {
    e.stopPropagation();
    onAddToCart?.(product);
  };

  return (
    <div className="product-card card-interactive" onClick={() => onClick?.(product)} id={`product-${product.id}`}>
      <div className="product-card-image-wrapper">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="product-card-image" />
        ) : (
          <div className="product-card-placeholder">
            <span>{product.name?.[0]?.toUpperCase() || '?'}</span>
          </div>
        )}
        {product.now_amount > 0 && product.now_amount < 5 && (
          <span className="product-card-badge-stock">Осталось {product.now_amount}</span>
        )}
        {product.now_amount === 0 && (
          <span className="product-card-badge-out">Нет в наличии</span>
        )}
      </div>
      
      <div className="product-card-info">
        <div className="product-card-price-row">
          <span className="product-card-price">₽{Number(product.price).toLocaleString('ru-RU')}</span>
        </div>
        
        <h3 className="product-card-title" title={product.name}>{product.name}</h3>
        
        {product.description && (
          <p className="product-card-desc">{product.description}</p>
        )}
      </div>

      <div className="product-card-actions">
        {onAddToCart ? (
          <button 
            className="btn btn-primary product-card-btn" 
            onClick={handleAdd} 
            disabled={product.now_amount === 0}
            id={`add-to-cart-${product.id}`}
          >
            <HiOutlineShoppingCart size={20} />
            В корзину
          </button>
        ) : null}
      </div>
    </div>
  );
}
