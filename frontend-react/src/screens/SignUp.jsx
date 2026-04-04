import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';
import appLogo from '../assets/app_logo.jpg';

const SignUp = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const showToast = useToast();

    const handleSignUp = async () => {
        if (!name || !email || !password) {
            showToast('Please fill all fields', 'error');
            return;
        }

        // Email regex
        const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
        if (!emailRegex.test(email)) {
            showToast('Please enter a valid email address', 'error');
            return;
        }

        // Password complexity
        if (password.length < 8) {
            showToast('Password must be at least 8 characters long', 'error');
            return;
        }
        if (!/[A-Z]/.test(password)) {
            showToast('Password must contain at least one uppercase letter', 'error');
            return;
        }
        if (!/[a-z]/.test(password)) {
            showToast('Password must contain at least one lowercase letter', 'error');
            return;
        }
        if (!/[0-9]/.test(password)) {
            showToast('Password must contain at least one number', 'error');
            return;
        }
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            showToast('Password must contain at least one special character', 'error');
            return;
        }

        setLoading(true);

        try {
            const res = await ApiService.request('/signup', {
                method: 'POST',
                body: JSON.stringify({ name, email, password })
            });

            if (res.status === 'success') {
                // Pass state to next route (verify otp)
                ApiService.request('/resend_otp', {
                    method: 'POST',
                    body: JSON.stringify({ email })
                }).catch(e => console.error("OTP generation silent fail:", e));

                navigate('/verify_otp', { 
                    state: { email, subtitle: "Complete Your Registration" } 
                });
            } else {
                showToast(res.message || 'Error occurred', 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="screen container active">
            <button className="btn-text" onClick={() => navigate(-1)} style={{ alignSelf: 'flex-start' }}>&larr; Back</button>
            <div className="center-content" style={{ marginTop: '-40px' }}>
                <img 
                    src={appLogo} 
                    alt="Crickzo Logo" 
                    style={{
                        width: '80px', 
                        height: '80px', 
                        borderRadius: '16px',
                        marginBottom: '24px',
                        boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
                    }} 
                />
                <h1>Create Account</h1>
                <p className="subtitle">Join Crickzo today</p>
                
                <div className="form-group">
                    <input 
                        type="text" 
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="input-field" 
                        placeholder="Full Name" 
                    />
                </div>
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
                    className="btn btn-primary mt-4" 
                    onClick={handleSignUp}
                    disabled={loading}
                >
                    {loading ? 'Registering...' : 'Register'}
                </button>
            </div>
        </div>
    );
};

export default SignUp;
