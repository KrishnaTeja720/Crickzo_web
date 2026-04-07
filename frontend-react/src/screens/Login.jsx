import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import saveethaLogo from '../assets/saveetha_logo.png';
import sesLogo from '../assets/ses_logo.png';
import appLogo from '../assets/app_logo.jpg';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const { login } = useContext(AuthContext);
    const showToast = useToast();

    const handleLogin = async () => {
        if (!email || !password) {
            showToast('Please fill all fields', 'error');
            return;
        }

        setLoading(true);

        try {
            const res = await ApiService.request('/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            if (res.status === 'success') {
                login({ userId: res.user_id, userName: res.name, userEmail: email });
                showToast(`Welcome back, ${res.name}!`);
                navigate('/home');
            } else {
                showToast('Invalid credentials', 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            {/* Left Side: Brand Sidebar */}
            <div className="login-sidebar">
                <div className="login-sidebar-content">
                    <img src={appLogo} alt="Criczo Logo" className="login-sidebar-logo" />
                    <h1 style={{ fontSize: '32px', color: 'white', fontWeight: '800', marginBottom: '8px', letterSpacing: '1px' }}>
                        REAL-TIME CRICKET
                    </h1>
                    <h2 style={{ fontSize: '28px', color: '#3B82F6', fontWeight: '700', marginBottom: '24px' }}>
                        SCORE PREDICTION
                    </h2>
                    <p style={{ fontSize: '16px', opacity: 0.8, maxWidth: '380px', margin: '0 auto', lineHeight: '1.6' }}>
                        Live scoring, player management, and smart score predictions in one powerful platform.
                    </p>
                </div>

                <div className="login-sidebar-footer">
                    <p>© 2026 Criczo. Engineered for Excellence.</p>
                </div>
            </div>

            {/* Right Side: Login Form */}
            <div className="login-form-side" style={{ position: 'relative' }}>
                {/* Branding Logos moved to white side */}
                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1000 }}>
                    <img 
                        src={saveethaLogo} 
                        alt="Saveetha Logo" 
                        style={{ height: '80px', width: 'auto' }}
                    />
                    <img 
                        src={sesLogo} 
                        alt="SES Logo" 
                        style={{ height: '65px', width: 'auto' }}
                    />
                </div>
                <div className="login-form-wrapper">
                    <h2 className="login-title">Welcome Back</h2>
                    <p className="login-subtitle">Sign in to continue to Criczo</p>

                    <div className="premium-input-group">
                        <input 
                            type="email" 
                            className="premium-input" 
                            placeholder="Email Address" 
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="premium-input-group">
                        <input 
                            type="password" 
                            className="premium-input" 
                            placeholder="Password" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: 'var(--gray-text)', cursor: 'pointer' }}>
                            <input type="checkbox" style={{ width: '16px', height: '16px', accentColor: 'var(--primary-blue)' }} />
                            Remember me
                        </label>
                        <span 
                            style={{ fontSize: '14px', color: 'var(--primary-blue)', fontWeight: '600', cursor: 'pointer' }}
                            onClick={() => navigate('/forgot_password')}
                        >
                            Forgot Password?
                        </span>
                    </div>

                    <button 
                        className="btn-premium" 
                        onClick={handleLogin}
                        disabled={loading}
                    >
                        {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                    
                    <div style={{ marginTop: '32px', textAlign: 'center', fontSize: '15px' }}>
                        Don't have an account? <span style={{ color: 'var(--primary-blue)', fontWeight: '700', cursor: 'pointer' }} onClick={() => navigate('/signup')}>Sign Up</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
