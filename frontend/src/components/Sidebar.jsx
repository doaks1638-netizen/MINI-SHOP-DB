import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineViewGrid, HiOutlineShoppingBag, HiOutlineClipboardList, HiOutlineUser, HiOutlineCog, HiOutlineUsers, HiOutlineTag, HiOutlineShoppingCart, HiOutlineCollection, HiOutlineLogout, HiOutlineLogin } from 'react-icons/hi';
import './Sidebar.css';

export default function Sidebar({ isOpen, onClose }) {
  const { isAuthenticated, isAdmin, logout } = useAuth();

  const publicLinks = [
    { to: '/', icon: <HiOutlineViewGrid size={20} />, label: 'Каталог' },
  ];

  const userLinks = [
    { to: '/cart', icon: <HiOutlineShoppingBag size={20} />, label: 'Корзина' },
    { to: '/orders', icon: <HiOutlineClipboardList size={20} />, label: 'Заказы' },
    { to: '/profile', icon: <HiOutlineUser size={20} />, label: 'Профиль' },
  ];

  const adminLinks = [
    { to: '/admin', icon: <HiOutlineCog size={20} />, label: 'Dashboard' },
    { to: '/admin/products', icon: <HiOutlineTag size={20} />, label: 'Товары' },
    { to: '/admin/categories', icon: <HiOutlineCollection size={20} />, label: 'Категории' },
    { to: '/admin/orders', icon: <HiOutlineClipboardList size={20} />, label: 'Заказы' },
    { to: '/admin/users', icon: <HiOutlineUsers size={20} />, label: 'Пользователи' },
    { to: '/admin/carts', icon: <HiOutlineShoppingCart size={20} />, label: 'Корзины' },
  ];

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar glass-strong ${isOpen ? 'sidebar-open' : ''}`} id="sidebar">
        <div className="sidebar-content">
          {/* Public section — always visible */}
          <div className="sidebar-section">
            <span className="sidebar-section-title">Магазин</span>
            <nav className="sidebar-nav">
              {publicLinks.map(link => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end
                  className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                  onClick={onClose}
                >
                  {link.icon}
                  <span>{link.label}</span>
                </NavLink>
              ))}

              {isAuthenticated && userLinks.map(link => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                  onClick={onClose}
                >
                  {link.icon}
                  <span>{link.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {isAuthenticated && isAdmin && (
            <div className="sidebar-section">
              <span className="sidebar-section-title">Администрирование</span>
              <nav className="sidebar-nav">
                {adminLinks.map(link => (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    end={link.to === '/admin'}
                    className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                    onClick={onClose}
                  >
                    {link.icon}
                    <span>{link.label}</span>
                  </NavLink>
                ))}
              </nav>
            </div>
          )}

          <div className="sidebar-footer">
            {isAuthenticated ? (
              <button className="sidebar-link sidebar-logout" onClick={() => { logout(); onClose(); }} id="logout-btn">
                <HiOutlineLogout size={20} />
                <span>Выйти</span>
              </button>
            ) : (
              <Link to="/login" className="sidebar-link sidebar-login" onClick={onClose} id="sidebar-login-btn">
                <HiOutlineLogin size={20} />
                <span>Войти</span>
              </Link>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
