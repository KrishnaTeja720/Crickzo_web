import React, { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import appLogo from '../assets/app_logo.jpg';

const Splash = () => {
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (user) {
                navigate('/home');
            } else {
                navigate('/login');
            }
        }, 2000);

        return () => clearTimeout(timer);
    }, [navigate, user]);

    return (
        <div className="screen container active" style={{
            background: 'linear-gradient(to bottom, var(--bg-gradient-start), var(--bg-gradient-end))',
            color: 'white',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '20px'
        }}>
            <img 
                src={appLogo} 
                alt="Crickzo Logo" 
                style={{ 
                    width: '180px', 
                    height: 'auto', 
                    borderRadius: '24px',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
                }} 
            />
            <div style={{ textAlign: 'center' }}>
                <h1 style={{ color: 'white', fontSize: '48px', fontWeight: 800, margin: 0 }}>Crickzo</h1>
                <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>Live matches, real-time predictions</p>
            </div>
        </div>
    );
};

export default Splash;
