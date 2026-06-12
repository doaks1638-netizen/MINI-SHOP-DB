import { useAuth } from '../../context/AuthContext';
import { HiOutlineTag, HiOutlineCollection, HiOutlineClipboardList, HiOutlineUsers, HiOutlineShoppingCart } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import './AdminPages.css';

export default function AdminDashboard() {
  const { user } = useAuth();

  const cards = [
    { to: '/admin/products', icon: <HiOutlineTag size={28} />, label: 'Товары', desc: 'Создание, редактирование и удаление товаров', color: 'violet' },
    { to: '/admin/categories', icon: <HiOutlineCollection size={28} />, label: 'Категории', desc: 'Управление категориями товаров', color: 'cyan' },
    { to: '/admin/orders', icon: <HiOutlineClipboardList size={28} />, label: 'Заказы', desc: 'Просмотр и изменение статусов заказов', color: 'amber' },
    { to: '/admin/users', icon: <HiOutlineUsers size={28} />, label: 'Пользователи', desc: 'Управление аккаунтами пользователей', color: 'green' },
    { to: '/admin/carts', icon: <HiOutlineShoppingCart size={28} />, label: 'Корзины', desc: 'Просмотр корзин пользователей', color: 'pink' },
  ];

  return (
    <div className="admin-page animate-fadeIn">
      <div className="page-header">
        <h1>
          <span className="gradient-text">Админ</span>-панель
        </h1>
        <p>Добро пожаловать, {user?.name}!</p>
      </div>

      <div className="admin-dashboard-grid stagger">
        {cards.map(card => (
          <Link key={card.to} to={card.to} className={`admin-dash-card card card-interactive admin-card-${card.color}`} id={`admin-nav-${card.label}`}>
            <div className={`admin-dash-icon admin-icon-${card.color}`}>
              {card.icon}
            </div>
            <h3>{card.label}</h3>
            <p>{card.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
