import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const Home = () => {
    const [liveMatches, setLiveMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const showToast = useToast();

    useEffect(() => {
        const fetchMatches = async () => {
            const currentUserId = user?.userId || localStorage.getItem('user_id');
            // Allow fetch even if user_id is null/undefined, backend now handles it
            console.log(`[Home] Fetching matches for user: ${currentUserId || 'Guest'}`);
            setError(null);
            try {
                // Fetch both live and upcoming
                const [liveRes, upcomingRes] = await Promise.all([
                    ApiService.request(`/matches/live?user_id=${currentUserId}`),
                    ApiService.request(`/matches/upcoming?user_id=${currentUserId}`)
                ]);
                
                console.log("[Home] Live Matches:", liveRes);
                console.log("[Home] Upcoming Matches:", upcomingRes);
                
                // Combine them for the dashboard overview if needed, 
                // but let's keep them separate as per UI design
                setLiveMatches(liveRes || []);
                // We could also set a state for upcoming matches if there's a section for it
                // For now, let's just ensure live matches are shown correctly
                
            } catch (err) {
                console.error("[Home] Failed to load matches", err);
                setError(err.message || "Failed to connect to backend");
            } finally {
                setLoading(false);
            }
        };

        fetchMatches();
    }, [user]);

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="header-text">
                    <h2 style={{ marginBottom: '4px' }}>Dashboard Overview</h2>
                    <p className="subtitle">Welcome back, {user?.userName || 'User'}</p>
                </div>
                <div className="header-actions">
                     <button className="btn btn-primary" onClick={() => navigate('/create_match')} style={{ padding: '10px 20px', fontSize: '14px', width: 'auto' }}>
                        + New Match
                     </button>
                </div>
            </header>
            
            <div className="dashboard-content">
                <section className="dashboard-section">
                    <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <div className="section-title">Live Analytics</div>
                        <button 
                            className="btn-text" 
                            onClick={() => navigate('/my_matches', { state: { tab: 'live' } })}
                            style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary-blue)', padding: 0 }}
                        >
                            View All Matches ›
                        </button>
                    </div>
                    
                    <div className="live-matches-grid">
                        {loading ? (
                            <div className="glass-card card-empty pulse">Synchronizing live data...</div>
                        ) : error ? (
                            <div className="glass-card card-empty error-card" style={{ 
                                borderColor: 'var(--error)', 
                                backgroundColor: 'rgba(239, 68, 68, 0.05)',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '12px',
                                padding: '30px'
                            }}>
                                <div style={{ fontSize: '24px' }}>🔌</div>
                                <div style={{ fontWeight: 600, color: 'var(--error)' }}>Connection Issue</div>
                                <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', maxWidth: '400px', margin: '0 auto' }}>
                                    {error}. Check if the backend server is running.
                                </div>
                                <button 
                                    className="btn btn-secondary" 
                                    onClick={() => {
                                        setError(null);
                                        setLoading(true);
                                        window.location.reload(); 
                                    }}
                                    style={{ width: 'fit-content', margin: '8px auto 0' }}
                                >
                                    Retry Connection
                                </button>
                            </div>
                        ) : liveMatches.length === 0 ? (
                            <div className="glass-card card-empty">No active matches currently tracked.</div>
                        ) : (
                            <div className="matches-scroll-container">
                                {liveMatches.slice(0, 3).map((match, idx) => (
                                    <div key={idx} onClick={() => navigate(`/scoring/${match.match_id}`, { state: { matchConfig: match } })} className="glass-card match-card-pro">
                                        <div className="card-top">
                                            <div className="live-indicator">
                                                <div className="live-dot"></div>
                                                <span className="live-label">LIVE FEED</span>
                                            </div>
                                            <span className="format-tag">{match.format ? `${match.format} Overs` : 'T20'} • Inn {match.current_innings || 1}</span>
                                        </div>
                                            <div className="match-teams-pro">
                                                <div className="team-item">
                                                    <span className="team-name">{match.team_a || match.teamA}</span>
                                                    <span className="team-score">Inning 1: {match.current_innings === 2 ? `${match.inn1_runs || 0}/${match.inn1_wickets || 0}` : `${match.runs || 0}/${match.wickets || 0}`}</span>
                                                </div>
                                                <div className="vs-divider">vs</div>
                                                <div className="team-item">
                                                    <span className="team-name">{match.team_b || match.teamB}</span>
                                                    <span className="team-score">{match.current_innings === 2 ? `Inning 2: ${match.runs || 0}/${match.wickets || 0}` : 'Yet to bat'}</span>
                                                </div>
                                            </div>
                                        <div className="card-footer-pro">
                                            <span className="overs-count">{match.overs || '0.0'} Overs</span>
                                            <span className="venue-text">{match.format ? `${match.format} Overs` : (match.venue || 'Standard Pitch')}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </section>
                
                <section className="dashboard-section mt-8">
                    <div className="section-title" style={{ marginBottom: '16px' }}>Performance & History</div>
                    <div className="history-grid">
                        <div className="glass-card action-card-pro" onClick={() => navigate('/my_matches', { state: { tab: 'live' } })}>
                            <div className="action-icon">🕒</div>
                            <div className="action-info">
                                <div className="action-title">Match Archive</div>
                                <div className="action-subtitle">{liveMatches.length} tracking sessions</div>
                            </div>
                        </div>
                        
                        <div className="glass-card action-card-pro" onClick={() => navigate('/my_matches', { state: { tab: 'completed' } })}>
                            <div className="action-icon">📊</div>
                            <div className="action-info">
                                <div className="action-title">Historical Results</div>
                                <div className="action-subtitle">View detailed scorecards</div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Home;
