import React from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import BottomNavigation from './BottomNavigation';

const Layout = ({ children }) => {
    const location = useLocation();
    const noNavPaths = ['/login', '/signup', '/', '/splash', '/forgot_password', '/reset_password', '/verify_otp'];
    const hideNav = noNavPaths.includes(location.pathname);

    if (hideNav) {
        return <div className="main-content">{children}</div>;
    }

    return (
        <div className="app-shell">
            <Sidebar />
            <div className="main-content">
                <div className="content-wrapper">
                    {children}
                </div>
                <BottomNavigation />
            </div>
        </div>
    );
};

export default Layout;
