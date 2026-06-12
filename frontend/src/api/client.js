const API_BASE = '/api/v1';

function getTokens() {
  const access = localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refresh_token');
  return { access, refresh };
}

function setTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

let isRefreshing = false;
let refreshPromise = null;

async function refreshTokens() {
  if (isRefreshing) return refreshPromise;
  isRefreshing = true;

  refreshPromise = (async () => {
    const { refresh } = getTokens();
    if (!refresh) {
      clearTokens();
      throw new Error('No refresh token');
    }

    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: refresh }),
    });

    if (!res.ok) {
      clearTokens();
      throw new Error('Token refresh failed');
    }

    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  })();

  try {
    const token = await refreshPromise;
    return token;
  } finally {
    isRefreshing = false;
    refreshPromise = null;
  }
}

async function apiRequest(endpoint, options = {}) {
  const { access } = getTokens();
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  const headers = {
    ...options.headers,
  };

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }

  if (access) {
    headers['Authorization'] = `Bearer ${access}`;
  }

  let res = await fetch(url, { ...options, headers });

  // Auto-refresh on 401
  if (res.status === 401 && access) {
    try {
      const newToken = await refreshTokens();
      headers['Authorization'] = `Bearer ${newToken}`;
      res = await fetch(url, { ...options, headers });
    } catch {
      // Redirect to login
      window.location.href = '/login';
      throw new Error('Authentication required');
    }
  }

  if (res.status === 204) return null;

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    let msg = `HTTP ${res.status}`;
    if (error && typeof error === 'object') {
      if (Array.isArray(error.detail)) {
        msg = error.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
      } else if (error.detail) {
        msg = String(error.detail);
      } else if (error.message) {
        msg = String(error.message);
      }
    }
    throw new Error(msg);
  }

  return res.json();
}

export const api = {
  get: (endpoint) => apiRequest(endpoint, { method: 'GET' }),
  post: (endpoint, body) => apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  }),
  patch: (endpoint, body) => apiRequest(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(body),
  }),
  delete: (endpoint) => apiRequest(endpoint, { method: 'DELETE' }),
};

export { getTokens, setTokens, clearTokens, API_BASE };
