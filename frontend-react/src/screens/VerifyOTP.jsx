import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const VerifyOTP = () => {
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const location = useLocation();
    const showToast = useToast();
    
    const state = location.state || {};
    const email = state.email || '';
    const subtitle = state.subtitle || 'Complete Your Registration';

    const handleVerify = async () => {
        if (otp.length !== 6) {
            showToast('Please enter a valid 6-digit OTP', 'error');
            return;
        }

        setLoading(true);

        try {
            const res = await ApiService.request('/verify_otp', {
                method: 'POST',
                body: JSON.stringify({ email, otp })
            });

            if (res.status === 'verified') {
                if (subtitle === 'Verify Your Identity') {
                     navigate('/reset_password', { state: { email } });
                } else {
                     showToast('Account successfully verified. Please login.');
                     navigate('/login');
                }
            } else {
                showToast('Invalid OTP', 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        try {
            await ApiService.request('/resend_otp', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            showToast('OTP Resent successfully');
        } catch (err) {
            showToast(err.message, 'error');
        }
    };

    return (
        <div className="screen container active">
            <button className="btn-text" onClick={() => navigate(-1)} style={{ alignSelf: 'flex-start' }}>&larr; Back</button>
            <div className="center-content" style={{ marginTop: '-40px' }}>
                <h1>Verify Email</h1>
                <p className="subtitle">{subtitle}</p>
                
                <p style={{ textAlign: 'center', marginBottom: '24px' }}>
                    We've sent a 6-digit code to <br/><b>{email}</b>
                </p>

                <div className="form-group">
                    <input 
                        type="text" 
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                        className="input-field" 
                        placeholder="Enter OTP (e.g. 123456)" 
                        maxLength="6" 
                        style={{ textAlign: 'center', letterSpacing: '8px', fontSize: '24px' }}
                    />
                </div>
                
                <button 
                    className="btn btn-primary mt-4" 
                    onClick={handleVerify}
                    disabled={loading}
                >
                    {loading ? 'Verifying...' : 'Verify'}
                </button>
                
                <div className="row mt-4" style={{ justifyContent: 'center', gap: '8px' }}>
                    <span style={{ color: 'var(--gray-text)' }}>Didn't receive code?</span>
                    <button className="btn-text" onClick={handleResend}>Resend OTP</button>
                </div>
            </div>
        </div>
    );
};

export default VerifyOTP;
