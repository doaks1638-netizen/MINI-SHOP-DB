import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Plugin that intercepts the Google OAuth callback.
 * Google redirects to /api/v1/auth/google/callback with a code.
 * The backend returns JSON tokens, but since this is a browser redirect,
 * the user would see raw JSON. This plugin intercepts the response,
 * extracts tokens, and redirects to the frontend's /callback page.
 */
function authCallbackPlugin() {
  return {
    name: 'auth-callback-redirect',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (!req.url?.startsWith('/api/v1/auth/google/callback')) {
          return next();
        }

        try {
          const backendUrl = `http://localhost:8000${req.url}`;
          const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            },
          });

          if (!response.ok) {
            const errText = await response.text();
            console.error('Auth callback error:', response.status, errText);
            res.writeHead(302, { Location: '/login?error=auth_failed' });
            return res.end();
          }

          const tokens = await response.json();
          const params = new URLSearchParams({
            access_token: tokens.access_token,
            refresh_token: tokens.refresh_token,
          });

          res.writeHead(302, { Location: `/callback?${params.toString()}` });
          res.end();
        } catch (error) {
          console.error('Auth callback proxy error:', error);
          res.writeHead(302, { Location: '/login?error=server_error' });
          res.end();
        }
      });
    }
  };
}

export default defineConfig({
  plugins: [authCallbackPlugin(), react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
