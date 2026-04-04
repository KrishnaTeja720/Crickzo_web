import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const SetupMatch = () => {
    const { matchId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const showToast = useToast();

    console.log("SetupMatch initialized - matchId from URL:", matchId);

    // Normalize matchConfig – handles both camelCase (app-created) and snake_case (DB/website-created)
    const [config, setConfig] = useState(() => {
        const mc = location.state?.matchConfig || {};
        const finalId = matchId || mc.id || mc.match_id;
        return {
            id: finalId,
            teamA: mc.teamA || mc.team_a || 'Team A',
            teamB: mc.teamB || mc.team_b || 'Team B',
            tossWinner: mc.tossWinner || mc.toss || 'Team A',
            tossDecision: mc.tossDecision || mc.toss_decision || 'Batting',
            playersA: mc.playersA || [],
            playersB: mc.playersB || [],
        };
    });

    const [inputA, setInputA] = useState('');
    const [inputB, setInputB] = useState('');
    const [striker, setStriker] = useState('');
    const [nonStriker, setNonStriker] = useState('');
    const [bowler, setBowler] = useState('');
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);

    // Derive batting/bowling teams
    const isABatting = (config.tossWinner === 'Team A' && config.tossDecision === 'Batting') ||
        (config.tossWinner === 'Team B' && config.tossDecision === 'Bowling');

    const battingTeamName = isABatting ? config.teamA : config.teamB;
    const bowlingTeamName = isABatting ? config.teamB : config.teamA;
    const battingPlayers = isABatting ? config.playersA : config.playersB;
    const bowlingPlayers = isABatting ? config.playersB : config.playersA;

    // ─────────────────────────────────────────────────────────────
    // Fetch existing players from the DB when the screen loads.
    // This handles matches created on the Crickzo website where
    // players are already registered in the match_players table.
    // ─────────────────────────────────────────────────────────────
    const refreshPlayers = async () => {
        const mid = matchId || config.id;
        if (!mid) return;

        setFetching(true);
        try {
            const players = await ApiService.request(`/match/players/${mid}`);
            console.log("PLAYERS RESPONSE:", players);

            if (!players || players.length === 0) return;

            const teamAName = config.teamA.trim().toLowerCase();
            const teamBName = config.teamB.trim().toLowerCase();

            let playersA = [];
            let playersB = [];

            players.forEach(p => {
                const pTeam = (p.team_name || '').trim().toLowerCase();
                if (!pTeam) return;

                const isA = (pTeam === teamAName || pTeam === 'a');
                const isB = (pTeam === teamBName || pTeam === 'b');

                if (isA) playersA.push(p.player_name);
                else if (isB) playersB.push(p.player_name);
            });

            console.log("REFRESHED LISTS - A:", playersA, "B:", playersB);
            setConfig(prev => {
                // Merge to avoid losing immediate local additions while fixing categorization
                const mergedA = Array.from(new Set([...playersA, ...prev.playersA])).filter(name => {
                    // Remove if it's in the WRONG server list (this fixes the mis-categorization)
                    return !playersB.includes(name);
                });
                const mergedB = Array.from(new Set([...playersB, ...prev.playersB])).filter(name => {
                    return !playersA.includes(name);
                });
                return {
                    ...prev,
                    playersA: mergedA,
                    playersB: mergedB,
                };
            });
        } catch (err) {
            console.warn('Could not refresh players:', err.message);
        } finally {
            setFetching(false);
        }
    };

    useEffect(() => {
        refreshPlayers();
    }, [config.id]); // eslint-disable-line react-hooks/exhaustive-deps

    // ─────────────────────────────────────────────────────────────
    // Player management helpers
    // ─────────────────────────────────────────────────────────────
    const handleAddPlayerA = async () => {
        if (inputA.trim()) {
            if (config.playersA.length >= 11) {
                showToast(`Each team can have a maximum of 11 players`, 'error');
                return;
            }
            const playerName = inputA.trim();
            const nameRegex = /^[A-Za-z\s]+$/;
            if (!nameRegex.test(playerName)) {
                showToast('Player name must only contain alphabetical characters', 'warning');
                return;
            }
            const payload = {
                match_id: config.id,
                player_name: playerName,
                team: "A"
            };
            console.log("ADD PLAYER PAYLOAD:", payload);
            try {
                await ApiService.request('/match/add_player', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                setInputA('');
                // Optimized: Update local state immediately for speed
                setConfig(prev => ({ ...prev, playersA: [...prev.playersA, playerName] }));
                // Still refresh to sync with server
                await refreshPlayers();
            } catch (err) {
                showToast(`Failed to add player: ${err.message}`, 'error');
            }
        } else {
            showToast('Player name cannot be empty', 'error');
        }
    };

    const handleAddPlayerB = async () => {
        if (inputB.trim()) {
            if (config.playersB.length >= 11) {
                showToast(`Each team can have a maximum of 11 players`, 'error');
                return;
            }
            const playerName = inputB.trim();
            const nameRegex = /^[A-Za-z\s]+$/;
            if (!nameRegex.test(playerName)) {
                showToast('Player name must only contain alphabetical characters', 'warning');
                return;
            }
            const payload = {
                match_id: config.id,
                player_name: playerName,
                team: "B"
            };
            console.log("ADD PLAYER PAYLOAD:", payload);
            try {
                await ApiService.request('/match/add_player', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                setInputB('');
                // Optimized: Update local state immediately
                setConfig(prev => ({ ...prev, playersB: [...prev.playersB, playerName] }));
                await refreshPlayers();
            } catch (err) {
                showToast(`Failed to add player: ${err.message}`, 'error');
            }
        } else {
            showToast('Player name cannot be empty', 'error');
        }
    };

    const handleRemovePlayerA = async (idx) => {
        const playerName = config.playersA[idx];
        try {
            await ApiService.request('/match/remove_player', {
                method: 'POST',
                body: JSON.stringify({
                    match_id: config.id,
                    player_name: playerName,
                    team_name: config.teamA
                })
            });
            setConfig(prev => ({ ...prev, playersA: prev.playersA.filter((_, i) => i !== idx) }));
        } catch (err) {
            showToast(`Failed to remove player: ${err.message}`, 'error');
        }
    };

    const handleRemovePlayerB = async (idx) => {
        const playerName = config.playersB[idx];
        try {
            await ApiService.request('/match/remove_player', {
                method: 'POST',
                body: JSON.stringify({
                    match_id: config.id,
                    player_name: playerName,
                    team_name: config.teamB
                })
            });
            setConfig(prev => ({ ...prev, playersB: prev.playersB.filter((_, i) => i !== idx) }));
        } catch (err) {
            showToast(`Failed to remove player: ${err.message}`, 'error');
        }
    };

    // ─────────────────────────────────────────────────────────────
    // Start match
    // ─────────────────────────────────────────────────────────────
    const handleStartMatch = async () => {
        if (!striker || !nonStriker || !bowler) {
            showToast('Please select all starting players (Striker, Non-Striker, and Bowler)', 'error');
            return;
        }

        if (striker === nonStriker) {
            showToast('Striker and Non-Striker must be different players', 'error');
            return;
        }

        if (config.playersA.length !== 11 || config.playersB.length !== 11) {
            showToast('Both teams must have exactly 11 players to start the match.', 'error');
            return;
        }

        setLoading(true);

        try {
            // First, save the full player lists to the database
            await ApiService.request('/match/setup', {
                method: 'POST',
                body: JSON.stringify({
                    match_id: config.id,
                    team_a_players: config.playersA,
                    team_b_players: config.playersB
                })
            });

            const payload = {
                match_id: config.id,
                striker,
                non_striker: nonStriker,
                bowler
            };

            const res = await ApiService.request('/match/start', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (res.status === 'success') {
                showToast('Match Started!');
                const activeMatchConfig = { ...config, striker, nonStriker, bowler };
                console.log("Navigating to scoring with matchId:", config.id);
                navigate(`/scoring/${config.id}`, { state: { matchConfig: activeMatchConfig }, replace: true });
            } else {
                showToast(res.error || 'Failed to start match', 'error');
            }
        } catch (e) {
            showToast(e.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="screen container active">
            <div className="section-header">
                <button className="btn-text" onClick={() => showToast("Cannot go back. Match ID generated.", "error")} style={{ padding: 0 }}>&#8592; Back</button>
                <div className="section-title" style={{ fontSize: '16px' }}>Add Players</div>
                <div style={{ width: '40px' }}></div>
            </div>

            <div style={{ background: 'var(--light-blue)', padding: '12px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px' }}>
                {fetching
                    ? '⏳ Syncing with cloud...'
                    : 'Add players for both teams. They will appear in the dropdowns below immediately.'}
                <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
                    Match ID: {config.id} | A: {config.playersA.length} | B: {config.playersB.length}
                </div>
            </div>

            {/* Team A */}
            <h2 style={{ fontSize: '16px' }}>{config.teamA}</h2>
            <div className="row" style={{ marginBottom: '8px' }}>
                <input
                    type="text"
                    value={inputA}
                    onChange={e => setInputA(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAddPlayerA()}
                    className="input-field"
                    style={{ padding: '8px', flex: 1, marginRight: '8px' }}
                    placeholder="Player Name"
                />
                <button 
                    className="btn btn-primary" 
                    onClick={handleAddPlayerA} 
                    style={{ padding: '8px 16px', width: 'auto' }}
                    disabled={config.playersA.length >= 11}
                >
                    {config.playersA.length >= 11 ? 'Full' : 'Add'}
                </button>
            </div>
            <div style={{ marginBottom: '24px', minHeight: '40px' }}>
                {config.playersA.map((p, idx) => (
                    <div key={idx} className="team-chip" style={{ marginRight: '4px', display: 'inline-flex' }}>
                        👤 {p} <span style={{ marginLeft: '8px', cursor: 'pointer' }} onClick={() => handleRemovePlayerA(idx)}>❌</span>
                    </div>
                ))}
            </div>

            {/* Team B */}
            <h2 style={{ fontSize: '16px' }}>{config.teamB}</h2>
            <div className="row" style={{ marginBottom: '8px' }}>
                <input
                    type="text"
                    value={inputB}
                    onChange={e => setInputB(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAddPlayerB()}
                    className="input-field"
                    style={{ padding: '8px', flex: 1, marginRight: '8px' }}
                    placeholder="Player Name"
                />
                <button 
                    className="btn btn-primary" 
                    onClick={handleAddPlayerB} 
                    style={{ padding: '8px 16px', width: 'auto' }}
                    disabled={config.playersB.length >= 11}
                >
                    {config.playersB.length >= 11 ? 'Full' : 'Add'}
                </button>
            </div>
            <div style={{ marginBottom: '24px', minHeight: '40px' }}>
                {config.playersB.map((p, idx) => (
                    <div key={idx} className="team-chip" style={{ marginRight: '4px', display: 'inline-flex' }}>
                        👤 {p} <span style={{ marginLeft: '8px', cursor: 'pointer' }} onClick={() => handleRemovePlayerB(idx)}>❌</span>
                    </div>
                ))}
            </div>

            {/* Initial Match Setup */}
            <div className="form-group mt-4">
                <label>Striker ({battingTeamName})</label>
                <select value={striker} onChange={e => setStriker(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="">Select Striker from {battingTeamName}</option>
                    {battingPlayers.map((p, idx) => <option key={idx} value={p}>{p}</option>)}
                </select>
            </div>
            <div className="form-group">
                <label>Non-Striker ({battingTeamName})</label>
                <select value={nonStriker} onChange={e => setNonStriker(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="">Select Non-Striker from {battingTeamName}</option>
                    {battingPlayers.map((p, idx) => <option key={idx} value={p}>{p}</option>)}
                </select>
            </div>
            <div className="form-group mb-4">
                <label>Opening Bowler ({bowlingTeamName})</label>
                <select value={bowler} onChange={e => setBowler(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="">Select Bowler from {bowlingTeamName}</option>
                    {bowlingPlayers.map((p, idx) => <option key={idx} value={p}>{p}</option>)}
                </select>
            </div>

            <div style={{ paddingBottom: '40px' }}>
                <button 
                    className="btn btn-primary mt-4" 
                    onClick={handleStartMatch} 
                    disabled={loading || fetching || config.playersA.length !== 11 || config.playersB.length !== 11}
                >
                    {loading ? 'Starting...' : fetching ? 'Loading Players...' : (config.playersA.length === 11 && config.playersB.length === 11) ? 'Start Match' : 'Add 11 Players each to Start'}
                </button>
            </div>
        </div>
    );
};

export default SetupMatch;
