import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ApiService from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import appLogo from '../assets/app_logo.jpg';

const MyMatches = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const showToast = useToast();

    const [activeTab, setActiveTab] = useState(location.state?.tab || 'upcoming');
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedMatch, setSelectedMatch] = useState(null);
    const [matchDetails, setMatchDetails] = useState({ inn1: null, inn2: null, loading: false });

    useEffect(() => {
        setSelectedMatch(null);

        const fetchMatches = async () => {
            const currentUserId = user?.userId || localStorage.getItem('user_id');
            // Allow fetch even if user_id is null/undefined, backend now handles it
            console.log(`[MyMatches] Fetching matches for user: ${currentUserId || 'Guest'}, Tab: ${activeTab}`);
            setLoading(true);
            setError(null);
            try {
                let endpoint = '';
                if (activeTab === 'upcoming') {
                    endpoint = `/matches/upcoming?user_id=${currentUserId}`;
                } else if (activeTab === 'live') {
                    endpoint = `/matches/live?user_id=${currentUserId}`;
                } else {
                    endpoint = `/matches/completed?user_id=${currentUserId}`;
                }
                
                const res = await ApiService.request(endpoint);
                console.log(`[MyMatches] ${activeTab} matches received:`, res);
                setMatches(res || []);
            } catch (err) {
                console.error(`[MyMatches] Failed to fetch ${activeTab} matches`, err);
                setError(err.message || "Failed to connect to backend");
            } finally {
                setLoading(false);
            }
        };

        fetchMatches();
    }, [user, activeTab, showToast]);

    const handleMatchClick = async (match) => {
        const matchId = match.id || match.match_id;
        if (activeTab === 'live' || activeTab === 'upcoming') {
            navigate(`/scoring/${matchId}`, { state: { matchConfig: { ...match, id: matchId } } });
        } else {
            setSelectedMatch(match);
            setMatchDetails({ inn1: null, inn2: null, loading: true });
            try {
                const [inn1, inn2] = await Promise.all([
                    ApiService.request(`/match/score/${matchId}?innings=1`),
                    ApiService.request(`/match/score/${matchId}?innings=2`)
                ]);
                setMatchDetails({ inn1, inn2, loading: false });
            } catch (e) {
                console.error("Score fetch failed", e);
                setMatchDetails(prev => ({ ...prev, loading: false }));
            }
        }
    };

    if (selectedMatch) {
        return (
            <div className="dashboard-container">
                <header className="dashboard-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <button className="btn-text" onClick={() => setSelectedMatch(null)} style={{ padding: 0, fontSize: '24px' }}>&larr;</button>
                        <div>
                            <h2 style={{ marginBottom: 0 }}>Match Scorecard</h2>
                            <p style={{ fontSize: '12px', color: 'var(--gray-text)', margin: 0 }}>{selectedMatch.teamA || selectedMatch.team_a} vs {selectedMatch.teamB || selectedMatch.team_b}</p>
                        </div>
                    </div>
                    <div className="header-actions">
                        <button className="btn" onClick={() => navigate(`/scorecard/${selectedMatch.id || selectedMatch.match_id}`)}
                            style={{ width: 'auto', padding: '10px 24px', background: 'var(--primary-blue)', color: 'var(--white)', border: 'none' }}>
                            📊 Full Scorecard
                        </button>
                    </div>
                </header>

                <div className="result-layout" style={{ maxWidth: '900px', margin: '0 auto' }}>
                    <div className="glass-card mb-8" style={{ padding: '40px', textAlign: 'center', background: 'linear-gradient(135deg, var(--white), var(--light-blue))' }}>
                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏆</div>
                        <h2 style={{ fontSize: '28px', color: 'var(--primary-blue)', marginBottom: '8px' }}>
                            {selectedMatch.winner && selectedMatch.winner.toLowerCase().includes('draw') 
                                ? 'Match Drawn' 
                                : `${selectedMatch.winner || 'N/A'} won`}
                        </h2>
                        <p style={{ color: 'var(--gray-text)', fontSize: '14px' }}>Final Result &bull; {selectedMatch.venue || 'Standard Pitch'}</p>
                    </div>

                    <div className="glass-card" style={{ padding: '32px' }}>
                         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                                <div className="innings-col">
                                    <div style={{ fontSize: '12px', color: 'var(--gray-text)', fontWeight: 700, marginBottom: '12px', textTransform: 'uppercase' }}>1st Innings</div>
                                    <div style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>{selectedMatch.teamA || selectedMatch.team_a}</div>
                                    <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--primary-blue)', marginBottom: '16px' }}>
                                        {matchDetails.inn1?.runs || 0}/{matchDetails.inn1?.wickets || 0}
                                    </div>
                                    <div style={{ fontSize: '14px', color: 'var(--gray-text)' }}>
                                        {parseFloat(matchDetails.inn1?.overs || 0).toFixed(1)} Overs &bull; CRR {matchDetails.inn1?.crr?.toFixed(2) || '0.00'}
                                    </div>
                                </div>

                                <div className="innings-col" style={{ borderLeft: '1px solid var(--slate-100)', paddingLeft: '32px' }}>
                                    <div style={{ fontSize: '12px', color: 'var(--gray-text)', fontWeight: 700, marginBottom: '12px', textTransform: 'uppercase' }}>2nd Innings</div>
                                    <div style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>{selectedMatch.teamB || selectedMatch.team_b}</div>
                                    <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--primary-blue)', marginBottom: '16px' }}>
                                        {matchDetails.inn2?.runs || 0}/{matchDetails.inn2?.wickets || 0}
                                    </div>
                                    <div style={{ fontSize: '14px', color: 'var(--gray-text)' }}>
                                        {parseFloat(matchDetails.inn2?.overs || 0).toFixed(1)} Overs &bull; CRR {matchDetails.inn2?.crr?.toFixed(2) || '0.00'}
                                    </div>
                                </div>
                            </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div>
                    <h2 style={{ marginBottom: '4px' }}>Match Archive</h2>
                    <p style={{ fontSize: '14px', color: 'var(--gray-text)', margin: 0 }}>View and analyze your previous sessions</p>
                </div>
            </header>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '32px' }}>
                <button 
                    onClick={() => setActiveTab('upcoming')}
                    className={`btn ${activeTab === 'upcoming' ? 'btn-primary' : ''}`}
                    style={{ width: 'auto', padding: '10px 24px', background: activeTab === 'upcoming' ? '' : 'var(--white)', color: activeTab === 'upcoming' ? '' : 'var(--text-main)', borderColor: activeTab === 'upcoming' ? '' : 'var(--slate-200)' }}
                >
                    Upcoming
                </button>
                <button 
                    onClick={() => setActiveTab('live')}
                    className={`btn ${activeTab === 'live' ? 'btn-primary' : ''}`}
                    style={{ width: 'auto', padding: '10px 24px', background: activeTab === 'live' ? '' : 'var(--white)', color: activeTab === 'live' ? '' : 'var(--text-main)', borderColor: activeTab === 'live' ? '' : 'var(--slate-200)' }}
                >
                    Live Ongoing
                </button>
                <button 
                    onClick={() => setActiveTab('completed')}
                    className={`btn ${activeTab === 'completed' ? 'btn-primary' : ''}`}
                    style={{ width: 'auto', padding: '10px 24px', background: activeTab === 'completed' ? '' : 'var(--white)', color: activeTab === 'completed' ? '' : 'var(--text-main)', borderColor: activeTab === 'completed' ? '' : 'var(--slate-200)' }}
                >
                    Completed Results
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '24px' }}>
                {loading ? (
                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--gray-text)' }}>Querying database...</div>
                ) : error ? (
                    <div className="glass-card card-empty" style={{ gridColumn: '1 / -1', borderColor: 'var(--error)', backgroundColor: 'rgba(239, 68, 68, 0.1)', textAlign: 'center', padding: '40px' }}>
                        ⚠️ {error}. Please ensure backend and database are running.
                    </div>
                ) : matches.length === 0 ? (
                    <div className="glass-card" style={{ gridColumn: '1 / -1', padding: '60px', textAlign: 'center' }}>
                        <img 
                            src={appLogo} 
                            alt="Logo" 
                            style={{ width: '80px', height: '80px', borderRadius: '16px', marginBottom: '24px', opacity: 0.6 }} 
                        />
                        <h3>No {activeTab} matches found</h3>
                        <p style={{ color: 'var(--gray-text)' }}>Start a new match to build your history.</p>
                    </div>
                ) : (
                    matches.map((match, idx) => (
                        <div key={idx} onClick={() => handleMatchClick(match)} className="glass-card" style={{ padding: '24px', cursor: 'pointer', transition: 'transform 0.2s' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: activeTab === 'upcoming' ? 'var(--primary-blue)' : (activeTab === 'live' ? 'var(--error)' : 'var(--success)') }}></div>
                                    <span style={{ fontSize: '10px', fontWeight: 800, color: activeTab === 'upcoming' ? 'var(--primary-blue)' : (activeTab === 'live' ? 'var(--error)' : 'var(--success)'), textTransform: 'uppercase' }}>
                                        {activeTab === 'upcoming' ? 'Upcoming' : (activeTab === 'live' ? `Live • Inn ${match.current_innings || 1}` : 'Completed')}
                                    </span>
                                </div>
                                <span style={{ fontSize: '12px', color: 'var(--gray-text)' }}>{match.format ? `${match.format} Overs` : (match.venue || 'Standard')}</span>
                            </div>
                            
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 800 }}>{match.teamA || match.team_a}</div>
                                    {activeTab === 'live' && (
                                        <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-blue)' }}>
                                            {match.current_innings === 1 ? `${match.runs || 0}/${match.wickets || 0}` : `${match.inn1_runs || 0}/${match.inn1_wickets || 0}`}
                                        </div>
                                    )}
                                </div>
                                <div style={{ padding: '0 16px', fontWeight: 800, color: 'var(--slate-200)' }}>VS</div>
                                <div style={{ flex: 1, textAlign: 'right' }}>
                                    <div style={{ fontWeight: 800 }}>{match.teamB || match.team_b}</div>
                                    {activeTab === 'live' && (
                                        <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-blue)' }}>
                                            {match.current_innings === 2 ? `${match.runs || 0}/${match.wickets || 0}` : 'Yet to bat'}
                                        </div>
                                    )}
                                    {activeTab === 'completed' && <div style={{ fontSize: '12px', color: 'var(--success)', fontWeight: 700 }}>Winner</div>}
                                </div>
                            </div>

                            <div style={{ paddingTop: '16px', borderTop: '1px solid var(--slate-100)', display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--gray-text)' }}>
                                <span>{activeTab === 'live' ? `${match.overs || 0} Overs` : (activeTab === 'upcoming' ? 'Upcoming' : (match.winner || 'Completed'))}</span>
                                <span style={{ color: 'var(--primary-blue)', fontWeight: 600 }}>Scorecard ›</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MyMatches;
