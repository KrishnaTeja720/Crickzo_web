import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const showToast = useToast();

    const handleSendCode = async () => {
        if (!email) {
            showToast('Please enter your email', 'error');
            return;
        }

        setLoading(true);

        try {
            await ApiService.request('/forgot_password', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            
            navigate('/verify_otp', { 
                state: { email, subtitle: "Verify Your Identity" } 
            });
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
                <h1>Reset Password</h1>
                <p className="subtitle">Enter your email to receive an OTP</p>
                
                <div className="form-group">
                    <input 
                        type="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="input-field" 
                        placeholder="Email Address" 
                    />
                </div>
                
                <button 
                    className="btn btn-primary mt-4" 
                    onClick={handleSendCode}
                    disabled={loading}
                >
                    {loading ? 'Sending...' : 'Send Code'}
                </button>
            </div>
        </div>
    );
};

export default ForgotPassword;
