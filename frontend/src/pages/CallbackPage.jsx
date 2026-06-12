import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loader from '../components/Loader';

export default function CallbackPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // The Google callback returns tokens from the API
    // The API endpoint /api/v1/auth/google/callback returns the tokens directly
    // We need to handle the redirect flow:
    // 1. Google redirects to our API callback
    // 2. The API returns tokens in the response
    // Since this is a server redirect, we need to check if tokens are in query params or hash

    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');

    if (accessToken && refreshToken) {
      login(accessToken, refreshToken);
      navigate('/', { replace: true });
    } else {
      // If no tokens in URL, redirect to login
      navigate('/login', { replace: true });
    }
  }, [searchParams, login, navigate]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <Loader size="lg" text="Авторизация..." />
    </div>
  );
}
