import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { HiOutlineMail, HiOutlineCreditCard, HiOutlinePencil, HiOutlineTrash, HiOutlineShieldCheck } from 'react-icons/hi';
import './ProfilePage.css';

export default function ProfilePage() {
  const { user, refreshUser, logout, isAdmin, isCreator } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [picture, setPicture] = useState(user?.picture || '');
  const [topUpAmount, setTopUpAmount] = useState('');
  const [topUpLoading, setTopUpLoading] = useState(false);

  const handleSave = async () => {
    try {
      await api.patch('/users/me', { name, picture });
      await refreshUser();
      toast.success('Профиль обновлён');
      setEditing(false);
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleTopUp = async () => {
    const amount = parseFloat(topUpAmount);
    if (!amount || amount <= 0) {
      toast.warning('Введите корректную сумму');
      return;
    }
    setTopUpLoading(true);
    try {
      const result = await api.post('/users/me/balance', { update_amount: amount });
      toast.success(`Баланс пополнен! Новый баланс: ₽${Number(result.balance).toLocaleString('ru-RU')}`);
      await refreshUser();
      setTopUpAmount('');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setTopUpLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm('Вы уверены? Это действие нельзя отменить.')) return;
    try {
      await api.delete('/users/me');
      toast.info('Аккаунт деактивирован');
      logout();
      navigate('/login');
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (!user) return null;

  const roleLabels = { user: 'Пользователь', admin: 'Администратор', creator: 'Создатель' };

  return (
    <div className="profile-page animate-fadeIn">
      <div className="page-header">
        <h1>
          <span className="gradient-text">Профиль</span>
        </h1>
      </div>

      <div className="profile-grid">
        {/* User Info Card */}
        <div className="profile-card card">
          <div className="profile-avatar-section">
            <div className="profile-avatar">
              {user.picture ? (
                <img src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
              ) : (
                <span className="gradient-text">{user.name?.[0]}</span>
              )}
            </div>
            <div className="profile-avatar-info">
              {editing ? (
                <div className="profile-edit-fields">
                  <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Имя" />
                  <input className="input" value={picture} onChange={(e) => setPicture(e.target.value)} placeholder="URL фото" />
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn btn-primary btn-sm" onClick={handleSave}>Сохранить</button>
                    <button className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>Отмена</button>
                  </div>
                </div>
              ) : (
                <>
                  <h2 className="profile-name">{user.name}</h2>
                  <div className="profile-role">
                    <span className={`badge ${isCreator ? 'badge-pink' : isAdmin ? 'badge-amber' : 'badge-violet'}`}>
                      <HiOutlineShieldCheck size={12} />
                      {roleLabels[user.role] || user.role}
                    </span>
                  </div>
                  <button className="btn btn-ghost btn-sm" onClick={() => setEditing(true)}>
                    <HiOutlinePencil size={14} /> Редактировать
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="profile-details">
            <div className="profile-detail-item">
              <HiOutlineMail size={18} />
              <div>
                <span className="profile-detail-label">Email</span>
                <span className="profile-detail-value">{user.email}</span>
              </div>
            </div>
            <div className="profile-detail-item">
              <HiOutlineCreditCard size={18} />
              <div>
                <span className="profile-detail-label">Баланс</span>
                <span className="profile-detail-value profile-balance">
                  ₽{Number(user.balance).toLocaleString('ru-RU', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Top-up Card */}
        <div className="profile-card card">
          <h3 className="profile-card-title">💳 Пополнить баланс</h3>
          <p className="profile-card-desc">Добавьте средства на ваш счёт для покупок</p>
          <div className="topup-form">
            <div className="topup-presets">
              {[100, 500, 1000, 5000].map(val => (
                <button
                  key={val}
                  className={`btn btn-secondary btn-sm ${topUpAmount === String(val) ? 'btn-active' : ''}`}
                  onClick={() => setTopUpAmount(String(val))}
                >
                  ₽{val.toLocaleString()}
                </button>
              ))}
            </div>
            <div className="topup-input-group">
              <input
                type="number"
                className="input"
                placeholder="Введите сумму"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                min="0"
                step="0.01"
                id="topup-input"
              />
              <button
                className="btn btn-primary"
                onClick={handleTopUp}
                disabled={topUpLoading}
                id="topup-btn"
              >
                {topUpLoading ? 'Пополнение...' : 'Пополнить'}
              </button>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="profile-card card profile-danger-card">
          <h3 className="profile-card-title">⚠️ Опасная зона</h3>
          <p className="profile-card-desc">Деактивация аккаунта — необратимое действие</p>
          <button className="btn btn-danger" onClick={handleDeleteAccount} id="delete-account-btn">
            <HiOutlineTrash size={16} /> Деактивировать аккаунт
          </button>
        </div>
      </div>
    </div>
  );
}
