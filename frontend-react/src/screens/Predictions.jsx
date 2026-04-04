import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ApiService from '../services/api';
import '../index.css';
import '../css/predictions.css';

const Predictions = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const config = location.state?.matchConfig || null;

    const prevScoreRef = useRef(null);
    const prevWinRef = useRef(null);

    const [pred, setPred] = useState({
        isCalculating: true,
        winA: 50, winB: 50,
        totalRange: 'Calculating...',
        totalLabel: 'Projected Target',
        nextOver: '-', next5: '-',
        wicketChance: 0,
        bat1: { runs: '-', bound: '-', risk: '-' },
        bat2: { runs: '-', bound: '-', risk: '-' }
    });

    useEffect(() => {
        if (!config) {
            navigate('/home');
            return;
        }
        
        const fetchPred = async () => {
            try {
                const currentInnings = config.currentInnings || 1;
                const d = await ApiService.request(`/match/predictions/${config.id}?innings=${currentInnings}`);
                
                // DATA SOURCE VALIDATION & LOGGING (RULES 1, 7)
                console.log("WIN PROB:", d.winner_prediction);

                // ROBUST KEY MAPPING (FIXING THE "MISSING PROBABILITY" ERROR)
                let rawA, rawB;
                
                // 1. Precise Match
                if (d.winner_prediction?.[config.teamA] !== undefined) {
                    rawA = d.winner_prediction[config.teamA];
                }
                if (d.winner_prediction?.[config.teamB] !== undefined) {
                    rawB = d.winner_prediction[config.teamB];
                }

                // 2. Fallback: Loose Match (handling "Team A" vs "Team A ")
                if (rawA === undefined || rawB === undefined) {
                    console.warn("Attempting loose key match for team names...");
                    const keys = Object.keys(d.winner_prediction || {});
                    
                    const matchA = keys.find(k => k.trim().toLowerCase() === config.teamA.trim().toLowerCase());
                    const matchB = keys.find(k => k.trim().toLowerCase() === config.teamB.trim().toLowerCase());
                    
                    if (matchA) rawA = d.winner_prediction[matchA];
                    if (matchB) rawB = d.winner_prediction[matchB];
                }

                // 3. Last Resort: Use first two numeric entries
                if (rawA === undefined || rawB === undefined) {
                    console.error("Critical: Could not map probabilities by team name. Using defaults.");
                    const values = Object.values(d.winner_prediction || {}).filter(v => typeof v === 'number');
                    rawA = values[0] ?? 50;
                    rawB = values[1] ?? 50;
                }

                // NORMALIZE & CLAMP VALUES (RULE 2)
                let total = rawA + rawB;
                let aNorm = total > 0 ? (rawA / total) * 100 : 50;
                let bNorm = total > 0 ? (rawB / total) * 100 : 50;

                let fWinA = Math.max(2, Math.min(98, aNorm));
                let fWinB = Math.max(2, Math.min(98, bNorm));
                if (fWinA === 98) fWinB = 2;
                if (fWinB === 98) fWinA = 2;
                
                fWinA = Math.round(fWinA * 10) / 10;
                fWinB = Math.round((100 - fWinA) * 10) / 10;

                // DIAGNOSTIC CHECKS (RULES 3, 9)
                const cState = d.current_state;
                if (prevScoreRef.current && prevWinRef.current && cState) {
                    const dRuns = cState.runs - prevScoreRef.current.runs;
                    const dWkts = cState.wickets - prevScoreRef.current.wickets;
                    const dBalls = cState.balls - prevScoreRef.current.balls;
                    
                    if ((dRuns !== 0 || dWkts !== 0 || dBalls !== 0) && fWinA === prevWinRef.current.winA) {
                         console.error("Win probability not updating");
                    }
                    
                    if (dWkts > 0 && config.teamA === d.team_names.a && fWinA > prevWinRef.current.winA) {
                         console.error("Logic error: wickets increased but batting win prob increased.");
                    }
                    if (dRuns > 0 && dWkts === 0 && config.teamA === d.team_names.a && fWinA < prevWinRef.current.winA) {
                         console.error("Logic error: runs left decreased but batting win prob decreased.");
                    }
                }
                
                if (cState) prevScoreRef.current = cState;
                prevWinRef.current = { winA: fWinA, winB: fWinB };

                setPred({
                    isCalculating: false,
                    winA: fWinA,
                    winB: fWinB,
                    totalRange: d.projected_score?.range || '...',
                    totalLabel: d.projected_score?.label || 'Projected Total',
                    nextOver: d.next_over?.runs || '-',
                    next5: d.next_5_overs?.runs || '-',
                    wicketChance: d.wicket_probability || 0,
                    bat1: { 
                        name: d.batsman_forecast?.[0]?.name || config.striker || 'Striker',
                        runs: d.batsman_forecast?.[0]?.final_runs ?? '-',
                        bound: d.batsman_forecast?.[0]?.boundary_percent ?? '-',
                        risk: d.batsman_forecast?.[0]?.out_risk ?? '-'
                    },
                    bat2: { 
                        name: d.batsman_forecast?.[1]?.name || config.nonStriker || 'Non-Striker',
                        runs: d.batsman_forecast?.[1]?.final_runs ?? '-',
                        bound: d.batsman_forecast?.[1]?.boundary_percent ?? '-',
                        risk: d.batsman_forecast?.[1]?.out_risk ?? '-'
                    }
                });
            } catch (e) {
                console.error("Prediction connection error", e);
                // FAILSAFE (RULE 8)
                setPred(prev => ({ ...prev, isCalculating: true, totalRange: 'Offline' }));
            }
        };

        fetchPred();
        
        // Polling (RULE 3)
        const interval = setInterval(fetchPred, 2500);
        
        return () => {
            clearInterval(interval);
        };
    }, [config, navigate]);

    if (!config) return null;

    return (
        <div className="screen active" style={{ display: 'flex', flexDirection: 'column', background: '#F8FAFC' }}>
            <div className="pred-header">
                <button className="btn-text" onClick={() => navigate(-1)} style={{ color: 'white', padding: 0 }}>&larr;</button>
                <div style={{ flex: 1, textAlign: 'center', fontWeight: 'bold' }}>Match Predictor</div>
                <div style={{ width: '24px' }}></div>
            </div>

            <div className="pred-content">
                <div style={{ textAlign: 'center', marginBottom: '16px', fontSize: '14px', fontWeight: 'bold' }}>
                    {config.teamA} vs {config.teamB}
                </div>

                {/* Win Probability (Aligned with Scoring Screen) - RULES 4, 6, 8 */}
                <div className="pred-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <div className="pred-title" style={{ marginBottom: 0 }}>Match Winner Probability</div>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary-blue)', background: 'rgba(0, 122, 255, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>LIVE</div>
                    </div>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '15px', fontWeight: 700, marginBottom: '8px' }}>
                        <span style={{ color: 'var(--text-main)' }}>{config.teamA}: {pred.isCalculating ? 'Calculating...' : `${pred.winA}%`}</span>
                        <span style={{ color: 'var(--text-main)' }}>{config.teamB}: {pred.isCalculating ? 'Calculating...' : `${pred.winB}%`}</span>
                    </div>
                    
                    <div style={{ display: 'flex', height: '10px', borderRadius: '5px', overflow: 'hidden', marginTop: '10px' }}>
                        <div style={{ width: `${pred.winA}%`, backgroundColor: 'var(--primary-blue)', transition: 'width 1.2s ease-in-out' }}></div>
                        <div style={{ width: `${pred.winB}%`, backgroundColor: '#10B981', transition: 'width 1.2s ease-in-out' }}></div>
                    </div>
                </div>

                {/* Over Predictions */}
                <div style={{ display: 'flex', gap: '12px' }}>
                    <div className="pred-card mini-card">
                        <div className="mini-title">Next Over</div>
                        <div className="mini-value">{pred.nextOver} runs</div>
                    </div>
                    <div className="pred-card mini-card">
                        <div className="mini-title">Next 5 Overs</div>
                        <div className="mini-value">{pred.next5} runs</div>
                    </div>
                </div>

                {/* Projected Score */}
                <div className="pred-card mt-4" style={{ background: 'linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end))', color: 'white' }}>
                    <div style={{ opacity: 0.9, fontSize: '14px', marginBottom: '4px' }}>{pred.totalLabel}</div>
                    <div style={{ fontSize: '36px', fontWeight: 800 }}>{pred.totalRange}</div>
                </div>

                {/* Wicket Probability */}
                <div className="pred-card mt-4">
                     <div className="pred-title">Wicket Probability (Next 12 Balls)</div>
                     <div className="team-row" style={{ marginTop: '12px' }}>
                        <span style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--error)' }}>{pred.wicketChance}%</span>
                    </div>
                    <div className="progress-bg mt-4" style={{ background: '#FEE2E2' }}>
                        <div className="progress-fill" style={{ width: `${pred.wicketChance}%`, background: 'var(--error)' }}></div>
                    </div>
                </div>

                {/* Batsman Forecast */}
                 <div className="pred-title" style={{ marginTop: '24px', marginBottom: '12px' }}>Batsman Forecast</div>
                 
                 <div className="pred-card">
                    <div className="bat-forecast-name">{pred.bat1.name}</div>
                    <div className="bat-forecast-row">
                        <div className="bat-detail">
                            <div className="bat-label">Predicted Score</div>
                            <div className="bat-val">{pred.bat1.runs}</div>
                        </div>
                        <div className="bat-detail">
                            <div className="bat-label">Boundary %</div>
                            <div className="bat-val">{pred.bat1.bound}%</div>
                        </div>
                        <div className="bat-detail">
                            <div className="bat-label">Dismissal Risk</div>
                            <div className="bat-val" style={{ color: 'var(--error)' }}>{pred.bat1.risk}%</div>
                        </div>
                    </div>
                 </div>

                 <div className="pred-card mt-4 mb-8">
                    <div className="bat-forecast-name">{pred.bat2.name}</div>
                    <div className="bat-forecast-row">
                        <div className="bat-detail">
                            <div className="bat-label">Predicted Score</div>
                            <div className="bat-val">{pred.bat2.runs}</div>
                        </div>
                        <div className="bat-detail">
                            <div className="bat-label">Boundary %</div>
                            <div className="bat-val">{pred.bat2.bound}%</div>
                        </div>
                        <div className="bat-detail">
                            <div className="bat-label">Dismissal Risk</div>
                            <div className="bat-val" style={{ color: 'var(--error)' }}>{pred.bat2.risk}%</div>
                        </div>
                    </div>
                 </div>
            </div>
        </div>
    );
};

export default Predictions;
