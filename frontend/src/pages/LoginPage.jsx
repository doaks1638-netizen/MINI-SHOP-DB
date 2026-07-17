import { useState } from 'react';
import { HiOutlineShieldCheck, HiOutlineMail, HiOutlineLockClosed, HiOutlineUser } from 'react-icons/hi';
import { API_BASE, api } from '../api/client';
import './LoginPage.css';

export default function LoginPage() {
  const [tab, setTab] = useState('login');
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE}/auth/google/login`;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await api.post('/auth/registry', { name, email, password });
      setSuccess('На вашу почту отправлено письмо с ссылкой для подтверждения регистрации.');
      setTab('login');
      setEmail('');
      setPassword('');
      setName('');
    } catch (err) {
      setError(err.message || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginStep1 = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await api.post('/auth/login', { email, password });
      setStep(2);
      setSuccess('Код подтверждения отправлен на вашу почту.');
    } catch (err) {
      setError(err.message || 'Неверные данные для входа');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginStep2 = (e) => {
    e.preventDefault();
    if (!code || code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }
    window.location.href = `${API_BASE}/auth/code_callback?code=${code}`;
  };

  return (
    <div className="login-page">
      <div className="login-bg-effects">
        <div className="login-orb login-orb-1"></div>
        <div className="login-orb login-orb-2"></div>
        <div className="login-orb login-orb-3"></div>
      </div>

      <div className="login-card glass-strong animate-scaleIn">
        <div className="login-logo">
          <span className="gradient-text login-logo-text">M</span>
        </div>
        <h1 className="login-title">MINI-SHOP-DB</h1>
        <p className="login-subtitle">Добро пожаловать в премиальный магазин</p>

        {step === 1 && (
          <div className="login-tabs">
            <button className={`login-tab ${tab === 'login' ? 'active' : ''}`} onClick={() => { setTab('login'); setError(''); setSuccess(''); }}>Вход</button>
            <button className={`login-tab ${tab === 'register' ? 'active' : ''}`} onClick={() => { setTab('register'); setError(''); setSuccess(''); }}>Регистрация</button>
          </div>
        )}

        {error && <div className="login-alert error">{error}</div>}
        {success && <div className="login-alert success">{success}</div>}

        {tab === 'login' && step === 1 && (
          <form onSubmit={handleLoginStep1} className="login-form">
            <div className="form-group">
              <HiOutlineMail className="form-icon" />
              <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <HiOutlineLockClosed className="form-icon" />
              <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="login-btn primary-btn" disabled={loading}>
              {loading ? 'Загрузка...' : 'Войти'}
            </button>
          </form>
        )}

        {tab === 'login' && step === 2 && (
          <form onSubmit={handleLoginStep2} className="login-form">
            <p className="login-hint">Введите 6-значный код из письма</p>
            <div className="form-group">
              <HiOutlineLockClosed className="form-icon" />
              <input type="text" placeholder="Код подтверждения" value={code} onChange={e => setCode(e.target.value)} required maxLength={6} />
            </div>
            <button type="submit" className="login-btn primary-btn" disabled={loading}>
              Подтвердить код
            </button>
            <button type="button" className="login-btn text-btn" onClick={() => setStep(1)} disabled={loading}>
              Назад
            </button>
          </form>
        )}

        {tab === 'register' && step === 1 && (
          <form onSubmit={handleRegister} className="login-form">
            <div className="form-group">
              <HiOutlineUser className="form-icon" />
              <input type="text" placeholder="Имя" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <HiOutlineMail className="form-icon" />
              <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <HiOutlineLockClosed className="form-icon" />
              <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
            </div>
            <button type="submit" className="login-btn primary-btn" disabled={loading}>
              {loading ? 'Загрузка...' : 'Зарегистрироваться'}
            </button>
          </form>
        )}

        {step === 1 && (
          <>
            <div className="login-divider">
              <span>Или</span>
            </div>
            <button type="button" className="login-google-btn" onClick={handleGoogleLogin} id="google-login-btn">
              <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Войти через Google
            </button>
          </>
        )}

        <div className="login-secure">
          <HiOutlineShieldCheck size={16} />
          <span>Безопасная авторизация OAuth 2.0</span>
        </div>
      </div>
    </div>
  );
}
