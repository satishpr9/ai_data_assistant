// ============================================
// FILE: src/api.js (UPDATED WITH AUTH)
// ============================================
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Set auth header
const authHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ==================== AUTH API ====================

export const register = async (username, email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    return { success: true, user: data.user };
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const login = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    return { success: true, user: data.user };
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const isAuthenticated = () => {
  return !!getToken();
};

// ==================== CONVERSATION API ====================

export const getConversations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      headers: authHeaders(),
    });

    if (!response.ok) throw new Error('Failed to fetch conversations');
    return await response.json();
  } catch (err) {
    console.error('Error fetching conversations:', err);
    return [];
  }
};

export const createConversation = async (title = 'New Conversation') => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) throw new Error('Failed to create conversation');
    return await response.json();
  } catch (err) {
    console.error('Error creating conversation:', err);
    return null;
  }
};

export const getConversation = async (conversationId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
      { headers: authHeaders() }
    );

    if (!response.ok) throw new Error('Failed to fetch conversation');
    return await response.json();
  } catch (err) {
    console.error('Error fetching conversation:', err);
    return null;
  }
};

export const deleteConversation = async (conversationId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`,
      {
        method: 'DELETE',
        headers: authHeaders(),
      }
    );

    if (!response.ok) throw new Error('Failed to delete conversation');
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const updateConversationTitle = async (conversationId, title) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/title?title=${encodeURIComponent(title)}`,
      {
        method: 'PATCH',
        headers: authHeaders(),
      }
    );

    if (!response.ok) throw new Error('Failed to update title');
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
};

// ==================== STREAMING QUERY (WITH CONVERSATION) ====================

export const sendQueryStream = async (
  query,
  conversationId,
  onToken,
  onComplete,
  onError
) => {
  try {
    const url = conversationId
      ? `${API_BASE_URL}/ask/stream?conversation_id=${conversationId}`
      : `${API_BASE_URL}/ask/stream`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Stream request failed');
    }

    const contentType = response.headers.get('content-type');

    if (!contentType || !contentType.includes('text/event-stream')) {
      const data = await response.json();
      onComplete(data);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split('\n\n');
      buffer = events.pop() || '';

      for (const event of events) {
        if (!event.trim()) continue;

        const line = event.replace(/^data: /, '');
        if (!line) continue;

        try {
          const data = JSON.parse(line);

          if (data.type === 'token') {
            onToken(data.content);
          } else if (data.type === 'end') {
            onComplete({ mode: 'rag', success: true });
          } else if (data.type === 'error') {
            onError(data.content);
          }
        } catch (e) {
          console.error('Failed to parse SSE event:', e);
        }
      }
    }
  } catch (err) {
    onError(err.message);
  }
};

// ==================== FILE UPLOAD ====================

export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'Upload failed');
    }

    return await response.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

// ==================== INGEST BUSINESS DATA ====================

export const ingestBusinessData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ingest/mysql`, {
      method: 'POST',
      headers: authHeaders(),
    });

    if (!response.ok) throw new Error('Ingest failed');
    return await response.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

// ==================== TEST API CONNECTION ====================

export const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('API unreachable');
    return { success: true };
  } catch {
    return { success: false };
  }
};