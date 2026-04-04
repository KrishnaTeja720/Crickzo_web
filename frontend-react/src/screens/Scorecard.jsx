import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const Scorecard = () => {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const showToast = useToast();
    const [loading, setLoading] = useState(true);
    const [scorecard, setScorecard] = useState(null);
    const [matchDetails, setMatchDetails] = useState(null);

    useEffect(() => {
        fetchData();
    }, [matchId]);

    const fetchData = async () => {
        try {
            const [details, data] = await Promise.all([
                ApiService.request(`/match/details/${matchId}`),
                ApiService.request(`/match/scorecard/${matchId}`)
            ]);
            setMatchDetails(details);
            setScorecard(data);
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="center-content" style={{ height: '80vh' }}>
            <div className="loader"></div>
            <p style={{ marginTop: '16px', color: 'var(--gray-text)' }}>Fetching detailed stats...</p>
        </div>
    );

    if (!scorecard || !matchDetails) return (
        <div className="center-content" style={{ height: '80vh' }}>
            <p style={{ color: 'var(--gray-text)' }}>No scorecard data available for this match.</p>
            <button className="btn-text" onClick={() => navigate(-1)}>Go Back</button>
        </div>
    );

    const renderBattingTable = (battingData, teamName) => (
        <div className="glass-card mb-4" style={{ padding: '20px', overflowX: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, color: 'var(--text-main)', fontSize: '18px' }}>{teamName} Batting</h3>
                <span className="badge" style={{ background: 'var(--light-blue)', color: 'var(--primary-blue)', padding: '4px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 }}>INNINGS STATS</span>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '400px' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid var(--slate-200)', textAlign: 'left', fontSize: '12px', color: 'var(--gray-text)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        <th style={{ padding: '12px 8px' }}>Batsman</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>R</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>B</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>4s</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>6s</th>
                        <th style={{ padding: '12px 8px', textAlign: 'right' }}>SR</th>
                    </tr>
                </thead>
                <tbody>
                    {battingData.map((p, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--slate-50)', fontSize: '14px', transition: 'background 0.2s' }}>
                            <td style={{ padding: '12px 8px' }}>
                                <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{p.player_name}</div>
                                <div style={{ fontSize: '11px', color: p.status === 'DNB' ? 'var(--gray-text)' : 'var(--primary-blue)', fontWeight: 600 }}>{p.status}</div>
                            </td>
                            <td style={{ padding: '12px 8px', textAlign: 'center', fontWeight: 800, color: 'var(--primary-blue)' }}>{p.runs}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center', color: 'var(--text-muted)' }}>{p.balls}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>{p.fours}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>{p.sixes}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--gray-text)', fontWeight: 600 }}>
                                {p.balls > 0 ? ((p.runs / p.balls) * 100).toFixed(1) : '0.0'}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    const renderBowlingTable = (bowlingData, teamName) => (
        <div className="glass-card" style={{ padding: '20px', overflowX: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, color: 'var(--text-main)', fontSize: '18px' }}>{teamName} Bowling</h3>
                <span className="badge" style={{ background: 'var(--slate-100)', color: 'var(--gray-text)', padding: '4px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 700 }}>OPPONENT ATTACK</span>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '400px' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid var(--slate-200)', textAlign: 'left', fontSize: '12px', color: 'var(--gray-text)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        <th style={{ padding: '12px 8px' }}>Bowler</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>O</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>M</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>R</th>
                        <th style={{ padding: '12px 8px', textAlign: 'center' }}>W</th>
                        <th style={{ padding: '12px 8px', textAlign: 'right' }}>ER</th>
                    </tr>
                </thead>
                <tbody>
                    {bowlingData.map((p, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--slate-50)', fontSize: '14px' }}>
                            <td style={{ padding: '12px 8px', fontWeight: 700, color: 'var(--text-main)' }}>{p.player_name}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>{p.overs}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>{p.maidens}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center', fontWeight: 700 }}>{p.runs}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'center', color: 'var(--error)', fontWeight: 800 }}>{p.wickets}</td>
                            <td style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--gray-text)', fontWeight: 600 }}>
                                {p.overs > 0 ? (p.runs / parseFloat(p.overs)).toFixed(2) : '0.00'}
                            </td>
                        </tr>
                    ))}
                    {bowlingData.length === 0 && (
                        <tr>
                            <td colSpan="6" style={{ padding: '32px', textAlign: 'center', color: 'var(--gray-text)', fontStyle: 'italic', fontSize: '13px' }}>
                                No bowling stats recorded yet (bowlers shown only after giving runs)
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="container" style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn-text" onClick={() => navigate(-1)} style={{ padding: 0, fontSize: '24px', color: 'var(--text-main)' }}>&larr;</button>
                    <div>
                        <h1 style={{ margin: 0, fontSize: '28px' }}>Detailed Scorecard</h1>
                        <p style={{ margin: 0, color: 'var(--gray-text)', fontSize: '14px', fontWeight: 500 }}>
                            {matchDetails.team_a} <span style={{ color: 'var(--primary-blue)' }}>vs</span> {matchDetails.team_b} • {matchDetails.venue}
                        </p>
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--gray-text)', textTransform: 'uppercase', marginBottom: '4px' }}>Match Status</div>
                    <div className="glass-card" style={{ padding: '4px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <div className="live-dot" style={{ width: '6px', height: '6px' }}></div>
                        <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--error)' }}>{matchDetails.status?.toUpperCase() || 'LIVE'}</span>
                    </div>
                </div>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '32px' }}>
                <div className="scorecard-section">
                    <div style={{ marginBottom: '24px' }}>
                        {renderBattingTable(scorecard.team_a.batting, matchDetails.team_a)}
                    </div>
                    <div>
                        {renderBowlingTable(scorecard.team_b.bowling, matchDetails.team_b)}
                    </div>
                </div>

                <div className="scorecard-section">
                    <div style={{ marginBottom: '24px' }}>
                        {renderBattingTable(scorecard.team_b.batting, matchDetails.team_b)}
                    </div>
                    <div>
                        {renderBowlingTable(scorecard.team_a.bowling, matchDetails.team_a)}
                    </div>
                </div>
            </div>
            
            <footer style={{ marginTop: '48px', padding: '24px', textAlign: 'center', borderTop: '1px solid var(--slate-200)' }}>
                <button className="btn-text" onClick={() => navigate(-1)} style={{ fontWeight: 600 }}>Back to Scoring</button>
            </footer>
        </div>
    );
};

export default Scorecard;
