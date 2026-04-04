import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const ResetPassword = () => {
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const location = useLocation();
    const showToast = useToast();
    
    const email = location.state?.email || '';

    const handleReset = async () => {
        if (!password) {
            showToast('Please enter a new password', 'error');
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
            await ApiService.request('/reset_password', {
                method: 'POST',
                body: JSON.stringify({ email, new_password: password })
            });

            showToast('Password updated successfully. Please login.');
            navigate('/login');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="screen container active">
            <div className="center-content">
                <h1>New Password</h1>
                <p className="subtitle">Create a secure new password</p>
                
                <div className="form-group">
                    <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field" 
                        placeholder="New Password" 
                    />
                </div>
                
                <button 
                    className="btn btn-primary mt-4" 
                    onClick={handleReset}
                    disabled={loading}
                >
                    {loading ? 'Saving...' : 'Save Password'}
                </button>
            </div>
        </div>
    );
};

export default ResetPassword;
