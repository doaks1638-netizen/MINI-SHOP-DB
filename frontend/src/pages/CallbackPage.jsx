import { useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loader from '../components/Loader';
import { API_BASE } from '../api/client';

export default function CallbackPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [searchParams] = useSearchParams();
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === '/auth/callback') {
      const token = searchParams.get('token');
      if (token) {
        window.location.href = `${API_BASE}/auth/url_callback?token=${token}`;
      } else {
        navigate('/login', { replace: true });
      }
      return;
    }

    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');

    if (accessToken && refreshToken) {
      login(accessToken, refreshToken);
      navigate('/', { replace: true });
    } else {
      navigate('/login', { replace: true });
    }
  }, [searchParams, login, navigate, location]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <Loader size="lg" text="Авторизация..." />
    </div>
  );
}
