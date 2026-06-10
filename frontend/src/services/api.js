const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers,
  };
  
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }
  
  try {
    const response = await fetch(url, config);
    
    if (response.status === 204) {
      return null;
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      let message = 'An error occurred on the server.';
      if (data && data.detail) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          message = data.detail.map(err => {
            const field = err.loc ? err.loc.filter(l => l !== 'body').join('.') : '';
            return field ? `${field}: ${err.msg}` : err.msg;
          }).join(', ');
        } else if (typeof data.detail === 'object') {
          message = JSON.stringify(data.detail);
        }
      }
      throw new Error(message);
    }
    
    return data;
  } catch (err) {
    if (err.message && err.message.includes('Failed to fetch')) {
      throw new Error('Could not connect to the backend server. Make sure it is running.');
    }
    throw err;
  }
}

export const api = {
  auth: {
    login: async (username, password) => {
      const data = await request('/api/auth/login', {
        method: 'POST',
        body: { username, password },
      });
      localStorage.setItem('token', data.access_token);
      return data;
    },
    register: async (username, email, password) => {
      return request('/api/auth/register', {
        method: 'POST',
        body: { username, email, password },
      });
    },
    me: async () => {
      return request('/api/auth/me', {
        method: 'GET',
      });
    },
    logout: () => {
      localStorage.removeItem('token');
    }
  },
  scan: {
    manual: async (payload) => {
      return request('/api/scan/manual', {
        method: 'POST',
        body: payload,
      });
    },
    auto: async (username) => {
      return request('/api/scan/auto', {
        method: 'POST',
        body: { username },
      });
    }
  },
  history: {
    list: async () => {
      return request('/api/history', {
        method: 'GET',
      });
    },
    delete: async (id) => {
      return request(`/api/history/${id}`, {
        method: 'DELETE',
      });
    }
  }
};
export default api;
