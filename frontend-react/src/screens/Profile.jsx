import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import BottomNavigation from '../components/BottomNavigation';
import { useToast } from '../context/ToastContext';
import ApiService from '../services/api';

const Profile = () => {
    const { user, logout, updateUser } = useContext(AuthContext);
    const navigate = useNavigate();
    const showToast = useToast();

    // Modal States
    const [showSettings, setShowSettings] = useState(false);
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    
    // Form States
    const [editedName, setEditedName] = useState(user?.userName || '');
    const [editedEmail, setEditedEmail] = useState(user?.userEmail || '');
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleUpdateProfile = async () => {
        if (!editedName || !editedEmail) {
            showToast('Name and Email are required', 'error');
            return;
        }
        setLoading(true);
        try {
            const res = await ApiService.request('/user/update_profile', {
                method: 'POST',
                body: JSON.stringify({
                    user_id: user.userId,
                    name: editedName,
                    email: editedEmail
                })
            });
            if (res.status === 'success') {
                updateUser({ userName: editedName, userEmail: editedEmail });
                showToast('Profile updated successfully', 'success');
                setShowSettings(false);
            } else {
                showToast(res.message || 'Update failed', 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleChangePassword = async () => {
        if (!oldPassword || !newPassword || !confirmPassword) {
            showToast('Please fill all password fields', 'error');
            return;
        }
        if (newPassword !== confirmPassword) {
            showToast('Passwords do not match', 'error');
            return;
        }
        setLoading(true);
        try {
            const res = await ApiService.request('/user/change_password', {
                method: 'POST',
                body: JSON.stringify({
                    user_id: user.userId,
                    old_password: oldPassword,
                    new_password: newPassword
                })
            });
            if (res.status === 'success') {
                showToast('Password updated successfully', 'success');
                setShowPasswordModal(false);
                setOldPassword('');
                setNewPassword('');
                setConfirmPassword('');
            } else {
                showToast(res.message || 'Password update failed', 'error');
            }
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    const initials = user?.userName?.length >= 2 ? user.userName.substring(0, 2).toUpperCase() : 'CF';

    return (
        <div className="dashboard-container active">
            <header className="dashboard-header">
                <div>
                    <h2 style={{ marginBottom: '4px' }}>My Account</h2>
                    <p className="subtitle">Manage your profile and preferences</p>
                </div>
                <div className="header-actions">
                     <button className="btn btn-outline danger" onClick={handleLogout} style={{ padding: '10px 20px', fontSize: '14px', width: 'auto' }}>
                        🚪 Logout
                     </button>
                </div>
            </header>

            <div className="profile-dashboard-layout" style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '32px' }}>
                <div className="profile-identity-col">
                    <div className="glass-card" style={{ padding: '32px', textAlign: 'center' }}>
                         <div className="profile-avatar-large" style={{ margin: '0 auto 24px' }}>{initials}</div>
                         <h3 style={{ fontSize: '20px', fontWeight: 800 }}>{user?.userName || 'User Name'}</h3>
                         <p style={{ color: 'var(--gray-text)', fontSize: '14px', marginBottom: '24px' }}>{user?.userEmail || 'user@example.com'}</p>
                         
                         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div className="glass-card" style={{ padding: '12px', background: 'var(--slate-50)' }}>
                                <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-blue)' }}>24</div>
                                <div style={{ fontSize: '10px', color: 'var(--gray-text)', textTransform: 'uppercase', fontWeight: 700 }}>Matches</div>
                            </div>
                            <div className="glass-card" style={{ padding: '12px', background: 'var(--slate-50)' }}>
                                <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--success)' }}>87%</div>
                                <div style={{ fontSize: '10px', color: 'var(--gray-text)', textTransform: 'uppercase', fontWeight: 700 }}>Accuracy</div>
                            </div>
                         </div>
                    </div>
                </div>

                <div className="profile-settings-col">
                    <section>
                        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px' }}>Account Settings</h3>
                        <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                                <span style={{ fontSize: '18px', color: 'var(--primary-blue)' }}>👤</span>
                                <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}>Profile Information</h4>
                            </div>
                            
                            <div className="form-group">
                                <label style={{ fontSize: '12px', color: 'var(--gray-text)', marginBottom: '4px', display: 'block' }}>Full Name</label>
                                <input 
                                    className="input-field" 
                                    value={editedName} 
                                    onChange={e => setEditedName(e.target.value)}
                                    placeholder="Enter your name"
                                    style={{ padding: '12px', fontSize: '14px' }}
                                />
                            </div>
                            <div className="form-group">
                                <label style={{ fontSize: '12px', color: 'var(--gray-text)', marginBottom: '4px', display: 'block' }}>Email Address</label>
                                <input 
                                    className="input-field" 
                                    value={editedEmail} 
                                    onChange={e => setEditedEmail(e.target.value)}
                                    placeholder="Enter your email"
                                    style={{ padding: '12px', fontSize: '14px' }}
                                />
                            </div>
                            
                            <button className="btn btn-primary" onClick={handleUpdateProfile} disabled={loading} style={{ padding: '12px', fontSize: '14px', marginTop: '8px' }}>
                                {loading ? 'Saving...' : 'Update Profile'}
                            </button>
                        </div>

                        <div className="glass-card" style={{ overflow: 'hidden' }}>
                            <div className="action-row-pro" onClick={() => setShowPasswordModal(true)} style={{ display: 'flex', alignItems: 'center', padding: '20px', borderBottom: '1px solid var(--slate-100)', cursor: 'pointer' }}>
                                <span style={{ fontSize: '24px', marginRight: '20px' }}>🛡️</span>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 700 }}>Security & Privacy</div>
                                    <div style={{ fontSize: '12px', color: 'var(--gray-text)' }}>Password and sensitive account details</div>
                                </div>
                                <span>›</span>
                            </div>
                            <div className="action-row-pro" onClick={() => navigate('/my_matches')} style={{ display: 'flex', alignItems: 'center', padding: '20px', cursor: 'pointer' }}>
                                <span style={{ fontSize: '24px', marginRight: '20px' }}>📜</span>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 700 }}>Tracking History</div>
                                    <div style={{ fontSize: '12px', color: 'var(--gray-text)' }}>View all your previous scoring sessions</div>
                                </div>
                                <span>›</span>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
            
            <footer style={{ marginTop: '40px', textAlign: 'center', color: 'var(--gray-text)', fontSize: '12px' }}>
                Criczo Premium Web v1.0.0 &bull; Professional Scoring Infrastructure
            </footer>

            {/* Account Settings Modal removed as per 'make it full' request */}

            {/* Change Password Modal */}
            {showPasswordModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', 
                    alignItems: 'center', justifyContent: 'center', zIndex: 1100,
                    backdropFilter: 'blur(4px)'
                }}>
                    <div className="glass-card" style={{
                        width: '90%', maxWidth: '400px', backgroundColor: 'white',
                        padding: '24px', borderRadius: '24px'
                    }}>
                        <h3 style={{ marginBottom: '8px' }}>Change Password</h3>
                        <p style={{ fontSize: '14px', color: 'var(--gray-text)', marginBottom: '20px' }}>
                            Ensure your account stays secure with a strong password.
                        </p>

                        <div className="form-group" style={{ position: 'relative' }}>
                            <label>Old Password</label>
                            <input 
                                className="input-field" type={showPassword ? "text" : "password"} 
                                value={oldPassword} onChange={e => setOldPassword(e.target.value)}
                                autoComplete="new-password"
                            />
                            <span 
                                onClick={() => setShowPassword(!showPassword)}
                                style={{ position: 'absolute', right: '12px', top: '38px', cursor: 'pointer', fontSize: '18px' }}
                            >
                                {showPassword ? '👁️' : '👁️‍🗨️'}
                            </span>
                        </div>
                        <div className="form-group" style={{ position: 'relative' }}>
                            <label>New Password</label>
                            <input 
                                className="input-field" type={showNewPassword ? "text" : "password"} 
                                value={newPassword} onChange={e => setNewPassword(e.target.value)}
                                autoComplete="new-password"
                            />
                            <span 
                                onClick={() => setShowNewPassword(!showNewPassword)}
                                style={{ position: 'absolute', right: '12px', top: '38px', cursor: 'pointer', fontSize: '18px' }}
                            >
                                {showNewPassword ? '👁️' : '👁️‍🗨️'}
                            </span>
                        </div>
                        <div className="form-group" style={{ position: 'relative' }}>
                            <label>Confirm New Password</label>
                            <input 
                                className="input-field" type={showConfirmPassword ? "text" : "password"} 
                                value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)}
                                autoComplete="new-password"
                            />
                            <span 
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                style={{ position: 'absolute', right: '12px', top: '38px', cursor: 'pointer', fontSize: '18px' }}
                            >
                                {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
                            </span>
                        </div>

                        <div style={{ textAlign: 'right', marginTop: '-12px', marginBottom: '16px' }}>
                            <span 
                                onClick={() => showToast('Forgot password flow coming soon', 'info')}
                                style={{ color: 'var(--primary-blue)', fontSize: '13px', cursor: 'pointer', fontWeight: 600 }}
                            >
                                Forgot Password?
                            </span>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '24px' }}>
                            <button className="btn btn-outline" onClick={() => setShowPasswordModal(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleChangePassword} disabled={loading}>
                                {loading ? 'Updating...' : 'Update'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;
