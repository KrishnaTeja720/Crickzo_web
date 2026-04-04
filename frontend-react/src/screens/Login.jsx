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
        <div className="screen container active">
            {/* Top Left Logo (Saveetha) */}
            <img 
                src={saveethaLogo} 
                alt="Saveetha Logo" 
                style={{
                    position: 'absolute',
                    top: '20px',
                    left: '20px',
                    width: '80px',
                    height: 'auto',
                    zIndex: 10
                }} 
            />
            {/* Top Right Logo (SES) */}
            <img 
                src={sesLogo} 
                alt="SES Logo" 
                style={{
                    position: 'absolute',
                    top: '20px',
                    right: '20px',
                    width: '60px',
                    height: 'auto',
                    zIndex: 10
                }} 
            />
            <div className="center-content">
                <img 
                    src={appLogo} 
                    alt="Crickzo Logo" 
                    style={{
                        width: '120px', 
                        height: '120px', 
                        borderRadius: '24px',
                        marginBottom: '24px',
                        boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
                    }} 
                />
                <h1>Welcome Back</h1>
                <p className="subtitle">Sign in to continue</p>
                
                <div className="form-group">
                    <input 
                        type="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="input-field" 
                        placeholder="Email Address" 
                    />
                </div>
                <div className="form-group">
                    <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field" 
                        placeholder="Password" 
                    />
                </div>
                
                <button 
                    className="btn btn-text" 
                    style={{ alignSelf: 'flex-end' }} 
                    onClick={() => navigate('/forgot_password')}
                >
                    Forgot Password?
                </button>
                
                <button 
                    className="btn btn-primary mt-4" 
                    onClick={handleLogin}
                    disabled={loading}
                >
                    {loading ? 'Signing In...' : 'Sign In'}
                </button>
                
                <div className="row mt-8" style={{ justifyContent: 'center', gap: '8px' }}>
                    <span style={{ color: 'var(--gray-text)' }}>Don't have an account?</span>
                    <button className="btn-text" onClick={() => navigate('/signup')}>Sign Up</button>
                </div>
            </div>
        </div>
    );
};

export default Login;
