import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import appLogo from '../assets/app_logo.jpg';

const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const path = location.pathname;

    const navItems = [
        { name: 'Home', path: '/home', icon: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z' },
        { name: 'Add Match', path: '/create_match', icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z' },
        { name: 'Premium', path: '/subscription', icon: 'M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-0.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z' },
        { name: 'Profile', path: '/profile', icon: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' }

    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header" style={{ marginBottom: '40px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <img 
                    src={appLogo} 
                    alt="Logo" 
                    style={{ width: '40px', height: '40px', borderRadius: '8px' }} 
                />
                <div>
                    <h1 style={{ color: 'var(--primary-blue)', margin: 0, fontSize: '20px' }}>Crickzo</h1>
                    <p style={{ fontSize: '12px', color: 'var(--gray-text)', margin: 0 }}>Cricket Scoring</p>
                </div>
            </div>
            
            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <div 
                        key={item.path}
                        className={`nav-item-sidebar ${path === item.path ? 'active' : ''}`}
                        onClick={() => navigate(item.path)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            cursor: 'pointer',
                            marginBottom: '8px',
                            fontWeight: '600',
                            transition: 'all 0.2s',
                            backgroundColor: path === item.path ? 'var(--light-blue)' : 'transparent',
                            color: path === item.path ? 'var(--primary-blue)' : 'var(--gray-text)'
                        }}
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path d={item.icon} />
                        </svg>
                        {item.name}
                    </div>
                ))}
            </nav>
            
            <div className="spacer"></div>
            
            <div className="sidebar-footer" style={{ fontSize: '10px', color: 'var(--gray-text)', textAlign: 'center' }}>
                &copy; 2026 Crickzo
            </div>
        </aside>
    );
};

export default Sidebar;
