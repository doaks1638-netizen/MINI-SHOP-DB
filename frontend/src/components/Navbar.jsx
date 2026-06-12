import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineShoppingBag } from 'react-icons/hi';
import './Navbar.css';

export default function Navbar({ onToggleSidebar, cartCount = 0 }) {
  const { user, isAuthenticated } = useAuth();

  return (
    <nav className="navbar glass-strong">
      <div className="navbar-left">
        <button className="navbar-toggle btn-icon btn-ghost" onClick={onToggleSidebar} id="sidebar-toggle">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>
        <Link to="/" className="navbar-brand" id="brand-link">
          <span className="navbar-logo gradient-text">M</span>
          <span className="navbar-title">MINI-SHOP-DB</span>
        </Link>
      </div>

      <div className="navbar-right">
        {isAuthenticated ? (
          <>
            <Link to="/cart" className="navbar-cart-btn btn-ghost btn-icon" id="cart-nav-btn">
              <HiOutlineShoppingBag size={22} />
              {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
            </Link>

            <div className="navbar-user" id="user-menu">
              <div className="navbar-user-info hide-mobile">
                <span className="navbar-user-name">{user?.name}</span>
                <span className="navbar-user-balance">₽{Number(user?.balance || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="navbar-avatar">
                {user?.picture ? (
                  <img src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
                ) : (
                  <span>{user?.name?.[0] || '?'}</span>
                )}
              </div>
            </div>
          </>
        ) : (
          <Link to="/login" className="btn btn-primary" id="login-nav-btn">Sign In</Link>
        )}
      </div>
    </nav>
  );
}
