import { useState } from 'react';
import { login, register } from '../api';
import './LoginSidebar.css';

function LoginSidebar({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let result;
      
      if (isLogin) {
        result = await login(formData.username, formData.password);
      } else {
        result = await register(
          formData.username,
          formData.email,
          formData.password
        );
      }

      if (result.success) {
        onAuthSuccess(result.user);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="login-sidebar-content">
      <div className="login-header">
        <div className="logo">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h2>AI Assistant</h2>
      </div>

      <div className="auth-tabs-minimal">
        <button
          className={isLogin ? 'active' : ''}
          onClick={() => {
            setIsLogin(true);
            setError('');
          }}
        >
          Log in
        </button>
        <button
          className={!isLogin ? 'active' : ''}
          onClick={() => {
            setIsLogin(false);
            setError('');
          }}
        >
          Sign up
        </button>
      </div>

      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-field">
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Username"
            required
            minLength={3}
          />
        </div>

        {!isLogin && (
          <div className="form-field">
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Email"
              required
            />
          </div>
        )}

        <div className="form-field">
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Password"
            required
            minLength={6}
          />
        </div>

        {error && <div className="login-error">{error}</div>}

        <button type="submit" className="login-submit" disabled={loading}>
          {loading ? (
            <span className="loading-spinner"></span>
          ) : (
            <span>{isLogin ? 'Continue' : 'Sign up'}</span>
          )}
        </button>
      </form>

      <div className="login-footer">
        <p className="terms">
          By continuing, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}

export default LoginSidebar;