import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const BottomNavigation = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const path = location.pathname;

    return (
        <div className="bottom-nav">
            <div 
                className={`nav-item ${path === '/home' ? 'active' : ''}`} 
                onClick={() => navigate('/home')}
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
                </svg>
                Home
            </div>
            <div 
                className={`nav-item ${path === '/create_match' ? 'active' : ''}`} 
                onClick={() => navigate('/create_match')}
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z" />
                </svg>
                Add Match
            </div>
            <div 
                className={`nav-item ${path === '/profile' ? 'active' : ''}`} 
                onClick={() => navigate('/profile')}
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
                Profile
            </div>
        </div>
    );
};

export default BottomNavigation;
