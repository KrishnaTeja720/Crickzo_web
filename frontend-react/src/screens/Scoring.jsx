import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import ApiService from '../services/api';
import { useToast } from '../context/ToastContext';

const Scoring = () => {
    const { matchId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const showToast = useToast();

    console.log("Scoring initialized - matchId from URL:", matchId);

    const [config] = useState(() => {
        const mc = location.state?.matchConfig;
        // Normalize field names: DB uses match_id/team_a/team_b, app uses id/teamA/teamB
        const finalId = mc?.id || mc?.match_id || matchId;
        const finalTeamA = mc?.teamA || mc?.team_a || 'Team A';
        const finalTeamB = mc?.teamB || mc?.team_b || 'Team B';
        console.log("Scoring initialized — ID:", finalId, "| TeamA:", finalTeamA, "| TeamB:", finalTeamB);
        if (mc) {
            return { ...mc, id: finalId, teamA: finalTeamA, teamB: finalTeamB };
        }
        // No state: only have the URL id; match details will be fetched via refreshScore
        return { id: finalId, teamA: finalTeamA, teamB: finalTeamB };
    });
    const [currentInnings, setCurrentInnings] = useState(1);
    const [scoreData, setScoreData] = useState({
        runs: 0, wickets: 0, overs: 0, crr: 0,
        strikingSide: 'A', // Track which team is batting
        strikerName: 'Loading...', strikerRuns: 0, strikerBalls: 0,
        nonStrikerName: 'Loading...', nonStrikerRuns: 0, nonStrikerBalls: 0,
        bowlerName: 'Loading...', bowlerRuns: 0, bowlerWickets: 0, bowlerOvers: 0,
        lastBowler: null,
        overEnded: false
    });
    const [partnership, setPartnership] = useState({ runs: 0, balls: 0 });
    const [timeline, setTimeline] = useState([]);
    const [error, setError] = useState(null);
    const [matchDetails, setMatchDetails] = useState({
        teamA: config.teamA || 'Team A',
        teamB: config.teamB || 'Team B',
        venue: config.venue || 'Match Venue',
        format: config.format || 'T20'
    });
    const [allPlayers, setAllPlayers] = useState(() => {
        const players = [];
        if (config.playersA) {
            config.playersA.forEach(name => players.push({ player_name: name, team_name: config.teamA }));
        }
        if (config.playersB) {
            config.playersB.forEach(name => players.push({ player_name: name, team_name: config.teamB }));
        }
        return players;
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showSelection, setShowSelection] = useState({ active: false, role: '', team: '' });
    const [manualName, setManualName] = useState('');
    const [pendingBall, setPendingBall] = useState(null);
    const [showExtraMenu, setShowExtraMenu] = useState(null); // 'WIDE' or 'NO_BALL'
    const [editScoreModal, setEditScoreModal] = useState({ active: false, runs: 0, wickets: 0, overs: '0.0' });
    const [outPlayers, setOutPlayers] = useState([]);
    const [showAllPlayersToggle, setShowAllPlayersToggle] = useState(false);
    
    // Scorecard State
    const [scorecardData, setScorecardData] = useState(null);
    const [showScorecard, setShowScorecard] = useState(false);
    const [scorecardTeamId, setScorecardTeamId] = useState('team_a');


    const fetchScorecard = async () => {
        const mid = matchId || config?.id;
        if (!mid) return;
        try {
            const data = await ApiService.request(`/match/scorecard/${mid}`);
            setScorecardData(data);
        } catch (err) {
            console.error("Scorecard fetch error:", err);
        }
    };

    const toggleScorecard = () => {
        if (!showScorecard) {
            fetchScorecard();
        }
        setShowScorecard(!showScorecard);
    };

    useEffect(() => {
        fetchMatchState();
    }, [matchId, currentInnings]);

    // Added to automatically refetch players when matchDetails is loaded
    useEffect(() => {
        if (matchDetails.teamA && matchDetails.teamA !== 'Team A') {
            fetchInitialData();
        }
    }, [matchDetails.teamA, matchDetails.teamB]);

    const fetchInitialData = async () => {
        const mid = config?.id || matchId;
        console.log("[DEBUG] fetchInitialData START for mid:", mid);
        if (!mid) return;
        try {
            const players = await ApiService.request(`/match/players/${mid}`);
            console.log("[DEBUG] MATCH PLAYERS fetched:", players);

            if (players && players.length > 0) {
                setAllPlayers(players);
            } else {
                // FALLBACK using latest matchDetails
                const tA = matchDetails?.teamA || config?.teamA;
                const tB = matchDetails?.teamB || config?.teamB;

                console.log("[DEBUG] Match roster empty. Fallback for:", tA, tB);
                if (tA && tA !== 'Team A') fetchGlobalPlayers(tA);
                if (tB && tB !== 'Team B') fetchGlobalPlayers(tB);
            }
        } catch (err) {
            console.warn("[DEBUG] Failed to fetch match players", err);
        }
    };

    const fetchGlobalPlayers = async (teamName) => {
        console.log("[DEBUG] fetchGlobalPlayers START for team:", teamName);
        if (!teamName || teamName === 'Team A' || teamName === 'Team B') return;
        try {
            const players = await ApiService.request(`/team/players/${teamName}`);
            console.log(`[DEBUG] GLOBAL PLAYERS for ${teamName} fetched:`, players);
            if (players && players.length > 0) {
                const formatted = players.map(p => ({ player_name: p.name, team_name: teamName }));
                setAllPlayers(prev => {
                    const existingNames = new Set(prev.map(p => p.player_name.toLowerCase()));
                    const newPlayers = formatted.filter(p => !existingNames.has(p.player_name.toLowerCase()));
                    console.log(`[DEBUG] Adding ${newPlayers.length} NEW players to state`);
                    return [...prev, ...newPlayers];
                });
                showToast(`Fetched ${players.length} players for ${teamName}`, 'success');
            } else {
                console.log(`[DEBUG] No global players found for ${teamName}`);
            }
        } catch (err) {
            console.warn('[DEBUG] Failed to fetch global team players', err);
        }
    };

    const fetchMatchState = async () => {
        const mid = matchId || config?.id;
        const userId = JSON.parse(localStorage.getItem('user'))?.userId;

        if (!mid) return;

        try {
            console.log("Fetching match state for matchId:", mid);
            const [matchState, recentBalls, partData] = await Promise.all([
                ApiService.request(`/match/state/${mid}?innings=${currentInnings}&user_id=${userId || 0}`),
                ApiService.request(`/match/last6/${mid}?innings=${currentInnings}`),
                ApiService.request(`/match/partnership/${mid}?innings=${currentInnings}`)
            ]);

            console.log("MATCH STATE:", matchState);
            console.log("RECENT BALLS:", recentBalls);
            console.log("PARTNERSHIP DATA:", partData);

            // Sync innings if backend says we are in a different innings than currently tracked in state
            if (matchState.current_innings && matchState.current_innings !== currentInnings) {
                console.log(`[Sync] Updating innings from ${currentInnings} to ${matchState.current_innings}`);
                setCurrentInnings(matchState.current_innings);
                return; // Dependency on currentInnings will trigger a re-fetch of correct innings data
            }

            setError(null);
            
            // Auto-refresh scorecard if open
            if (showScorecard) {
                fetchScorecard();
            }

            // Update Match Metadata
            setMatchDetails({
                teamA: matchState.team_a,
                teamB: matchState.team_b,
                tossWinner: matchState.toss_winner,
                tossDecision: matchState.toss_decision,
                venue: matchState.venue,
                format: matchState.format
            });

            setTimeline(recentBalls || []);
            setPartnership(partData || { runs: 0, balls: 0 });

            let balls = matchState.balls || 0;
            const crr = matchState.crr || 0;
            const runs = matchState.runs || 0;

            // Failsafe: Derive balls from CRR if balls is 0 but CRR exists
            if (balls === 0 && crr > 0 && runs > 0) {
                balls = Math.round((runs * 6) / crr);
            }

            const displayOvers = (matchState.overs && matchState.overs !== "0.0") 
                ? matchState.overs 
                : `${Math.floor(balls / 6)}.${balls % 6}`;



            // Robust Team Identification Logic
            const teamA = matchState.team_a || matchDetails.teamA;
            const teamB = matchState.team_b || matchDetails.teamB;
            const tossWinner = matchState.toss_winner || matchDetails.tossWinner;
            const tossDecision = matchState.toss_decision || matchDetails.tossDecision;

            let firstBatting = teamA;
            let firstBowling = teamB;

            if ((tossWinner === 'Team A' && tossDecision === 'Bowling') || 
                (tossWinner === 'Team B' && tossDecision === 'Batting') ||
                (tossWinner === teamA && tossDecision === 'Bowling') ||
                (tossWinner === teamB && tossDecision === 'Batting')) {
                firstBatting = teamB;
                firstBowling = teamA;
            }

            const currentBatting = currentInnings === 1 ? firstBatting : firstBowling;
            const currentBowling = currentInnings === 1 ? firstBowling : firstBatting;

            setScoreData({
                runs: matchState.runs || 0,
                wickets: matchState.wickets || 0,
                overs: displayOvers,
                balls: balls,
                crr: matchState.crr || 0,
                strikerName: matchState.striker || "Not Set",
                strikerRuns: matchState.striker_runs || 0,
                strikerBalls: matchState.striker_balls || 0,
                nonStrikerName: matchState.non_striker || "Not Set",
                nonStrikerRuns: matchState.non_striker_runs || 0,
                nonStrikerBalls: matchState.non_striker_balls || 0,
                bowlerName: matchState.bowler || "Not Set",
                bowlerRuns: matchState.bowler_runs || 0,
                bowlerWickets: matchState.bowler_wickets || 0,
                bowlerOvers: matchState.bowler_overs || "0.0",
                balls_in_over: balls % 6,
                battingTeam: matchState.batting_team || currentBatting,
                bowlingTeam: matchState.bowling_team || currentBowling,
                predictions: matchState.predictions || null,
                lastBowler: matchState.last_bowler,
                overEnded: matchState.over_ended
            });
            setOutPlayers(matchState.out_players || []);

            // AUTOMATIC SETUP PROMPT: Sequential selection for Striker -> Non-Striker -> Bowler
            if (matchState.wickets < 10) {
                if (!matchState.striker || matchState.striker === "Not Set" || matchState.striker === null) {
                    console.log("[DEBUG] Auto-triggering STRIKER selection");
                    setShowSelection({ active: true, role: 'striker', team: matchState.batting_team || currentBatting });
                } else if (!matchState.non_striker || matchState.non_striker === "Not Set" || matchState.non_striker === null) {
                    console.log("[DEBUG] Auto-triggering NON-STRIKER selection");
                    setShowSelection({ active: true, role: 'non_striker', team: matchState.batting_team || currentBatting });
                } else if (!matchState.bowler || matchState.bowler === "Not Set" || matchState.bowler === null || (matchState.over_ended && matchState.bowler === matchState.last_bowler)) {
                    console.log("[DEBUG] Auto-triggering BOWLER selection");
                    setShowSelection({ active: true, role: 'bowler', team: matchState.bowling_team || currentBowling });
                }
            }

        } catch (err) {
            console.error("[Refresh Sync Error]", err);
            setError(err.message.startsWith("Network error") ? "Network error: backend unreachable" : err.message);
        }
    };

    const handleUndo = async () => {
        const mid = matchId || config?.id;
        if (!mid) return;
        try {
            await ApiService.request(`/match/undo/${mid}`, { method: 'DELETE' });
            showToast('Last ball undone', 'success');
            await fetchMatchState();
        } catch (e) {
            showToast(e.message, 'error');
        }
    };

    const handleEditScore = () => {
        setEditScoreModal({
            active: true,
            runs: scoreData.runs,
            wickets: scoreData.wickets,
            overs: scoreData.overs || "0.0"
        });
    };

    const saveEditedScore = async () => {
        const mid = matchId || config?.id;
        try {
            const result = await ApiService.request('/match/edit_score', {
                method: 'POST',
                body: JSON.stringify({
                    match_id: mid,
                    innings: currentInnings,
                    runs: editScoreModal.runs,
                    wickets: editScoreModal.wickets,
                    overs: editScoreModal.overs
                })
            });

            if (result.status === 'error') {
                throw new Error(result.message || 'Server rejected edit');
            }

            setEditScoreModal({ ...editScoreModal, active: false });
            showToast('Score updated successfully', 'success');
            await fetchMatchState();
        } catch (e) {
            showToast('Score update failed: ' + e.message, 'error');
        }
    };

    const handleSwapStrikers = async () => {
        const mid = matchId || config?.id;
        try {
            const res = await ApiService.request('/match/swap_strikers', {
                method: 'POST',
                body: JSON.stringify({ match_id: mid })
            });

            if (res.status === 'success') {
                showToast('Strikers swapped', 'success');
                fetchMatchState(); // Refresh UI
            } else {
                showToast(res.error || 'Failed to swap strikers', 'error');
            }
        } catch (e) {
            showToast(e.message, 'error');
        }
    };

    const handleRefreshScore = async () => {
        const mid = matchId || config?.id;
        try {
            const result = await ApiService.request('/match/recompute_score', {
                method: 'POST',
                body: JSON.stringify({
                    match_id: mid,
                    innings: currentInnings
                })
            });

            if (result.status === 'success') {
                showToast('Score refreshed to actual calculations', 'success');
            } else {
                showToast('Refresh partially failed: ' + result.message, 'warning');
            }
            await fetchMatchState();
        } catch (e) {
            showToast('Score refresh failed: ' + e.message, 'error');
        }
    };

    const handlePlayerChange = async (playerName) => {
        if (isSubmitting) return;
        const mid = matchId || config?.id;
        setIsSubmitting(true);
        try {
            if (showSelection.role === 'wicket_replacement') {
                // Submit the ball that caused the wicket now that we have the new batsman
                const finalPayload = { ...pendingBall, new_batsman: playerName };
                await ApiService.request('/match/ball', {
                    method: "POST",
                    body: JSON.stringify(finalPayload)
                });
                showToast('Wicket recorded!', 'success');
                setPendingBall(null);
            } else if (showSelection.role === 'bowler') {
                await ApiService.request('/match/change_bowler', {
                    method: 'POST',
                    body: JSON.stringify({ match_id: mid, bowler: playerName })
                });
                showToast('Bowler updated', 'success');
            } else {
                await ApiService.request('/match/new_batsman', {
                    method: 'POST',
                    body: JSON.stringify({ match_id: mid, new_player: playerName, role: showSelection.role })
                });
                showToast(`${showSelection.role.replace('_', ' ')} updated`, 'success');
            }
            setShowSelection({ active: false, role: '', team: '' });
            await fetchMatchState();
        } catch (e) {
            showToast(e.message, 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleAction = async (value, type = "NONE", isWicket = false) => {
        if (isSubmitting) return;

        const mid = matchId || config?.id;
        if (!mid) return;

        // Ensure bowler and striker are set
        if (!scoreData.bowlerName || scoreData.bowlerName === "Not Set" || scoreData.bowlerName === "Loading...") {
            showToast("Please select a bowler first!", "error");
            setShowSelection({ active: true, role: 'bowler', team: scoreData.bowlingTeam });
            return;
        }

        if (!scoreData.strikerName || scoreData.strikerName === "Not Set" || scoreData.strikerName === "Loading...") {
            showToast("Please select a striker first!", "error");
            setShowSelection({ active: true, role: 'striker', team: scoreData.battingTeam });
            return;
        }

        setIsSubmitting(true);

        try {
            let batsmanRuns = value;
            let extras = 0;
            let extraType = null;

            if (type === "WIDE") { extraType = "wide"; extras = 1 + value; batsmanRuns = value; }
            else if (type === "NO_BALL") { extraType = "no_ball"; extras = 1; batsmanRuns = value; }
            else if (type === "BYE") { extraType = "bye"; extras = value; batsmanRuns = value; }
            else if (type === "LEG_BYE") { extraType = "legbye"; extras = value; batsmanRuns = value; }
            else if (type === "PENALTY") { extraType = "penalty"; extras = value; batsmanRuns = value; }

            let newBatsman = null;
            if (isWicket) {
                const payload = {
                    match_id: mid,
                    innings: currentInnings,
                    batsman: scoreData.strikerName,
                    bowler: scoreData.bowlerName,
                    runs: batsmanRuns,
                    extras: extras,
                    extra_type: extraType,
                    wicket: 1,
                    is_wicket: true,
                    new_batsman: null,
                    out_batsman: null // Will be set in the next step
                };
                setPendingBall(payload);
                setShowSelection({
                    active: true,
                    role: 'wicket_out_selection',
                    team: scoreData.battingTeam,
                });
                setIsSubmitting(false);
                return;
            }

            const payload = {
                match_id: mid,
                innings: currentInnings,
                batsman: scoreData.strikerName,
                bowler: scoreData.bowlerName,
                runs: batsmanRuns,
                extras: extras,
                extra_type: extraType,
                wicket: isWicket ? 1 : 0,
                is_wicket: isWicket,
                new_batsman: newBatsman
            };

            console.log("BALL PAYLOAD:", payload);

            const data = await ApiService.request('/match/ball', {
                method: "POST",
                body: JSON.stringify(payload)
            });

            console.log("BALL RESPONSE:", data);
            showToast(isWicket ? 'Wicket recorded!' : 'Ball recorded', 'success');

            // Immediately refresh state
            await fetchMatchState();
        } catch (e) {
            console.error("Ball submission failed:", e);
            showToast(e.message, 'error');
            await fetchMatchState();
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleEndInnings = async () => {
        const msg = currentInnings === 1
            ? "Are you sure you want to end the 1st innings?"
            : "Are you sure you want to end the match?";

        if (window.confirm(msg)) {
            if (currentInnings === 1) {
                const mid = matchId || config?.id;
                try {
                    await ApiService.request('/match/update_innings', {
                        method: 'POST',
                        body: JSON.stringify({ match_id: mid, innings: 2 })
                    });
                    
                    // Reset local score state for UI clarity
                    setScoreData(prev => ({
                        ...prev,
                        runs: 0, wickets: 0, overs: "0.0", balls: 0, crr: 0,
                        strikerName: 'Not Set', nonStrikerName: 'Not Set', bowlerName: 'Not Set'
                    }));
                    
                    setCurrentInnings(2);
                    showToast('Starting 2nd Innings', 'success');
                    await fetchMatchState();
                } catch (e) {
                    showToast("Failed to sync innings: " + e.message, 'error');
                }
            } else {
                handleEndMatch();
            }
        }
    };

    const handleEndMatch = async () => {
        if (!config) return;
        try {
            let winner = 'Draw';
            if (currentInnings === 1) {
                winner = config.teamA + " (Innings 1 end)";
            } else {
                // Fetch 1st innings score to compare
                const inn1 = await ApiService.request(`/match/score/${config.id}?innings=1`);
                const runs1 = inn1.runs || 0;
                const runs2 = scoreData.runs || 0;

                if (runs1 > runs2) winner = config.teamA;
                else if (runs2 > runs1) winner = config.teamB;
                else winner = 'Draw';
            }

            await ApiService.request('/match/end', {
                method: 'POST',
                body: JSON.stringify({ match_id: config.id, winner: winner })
            });
            showToast('Match completed', 'success');
            navigate('/home');
        } catch (e) {
            showToast(e.message, 'error');
        }
    };

    if (!config) return null;

    return (
        <div className="dashboard-container">
            <header className="dashboard-header" style={{ alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn-text" onClick={() => navigate('/home')} style={{ padding: 0, fontSize: '24px' }}>&larr;</button>
                    <div>
                        <h2 style={{ marginBottom: 0 }}>{matchDetails.teamA} vs {matchDetails.teamB}</h2>
                        <p style={{ fontSize: '12px', color: 'var(--gray-text)', margin: 0 }}>Innings {currentInnings} • {matchDetails.venue}</p>
                    </div>
                </div>
                <div className="header-actions" style={{ display: 'flex', gap: '12px' }}>
                    <button 
                        className="btn-text" 
                        onClick={() => navigate(`/scorecard/${matchId}`)}
                        style={{ background: 'var(--white)', padding: '8px 16px', borderRadius: '12px', fontSize: '12px', fontWeight: 700, border: '1px solid var(--slate-200)', color: 'var(--text-main)' }}
                    >
                        📊 Full Scorecard
                    </button>
                    <div className="glass-card" style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div className="live-dot"></div>
                        <span style={{ fontWeight: 800, fontSize: '12px', color: 'var(--error)' }}>MATCH LIVE</span>
                    </div>
                </div>
            </header>

            <div className="scoring-layout" style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
                <div className="scoring-main-col">
                    {error && (
                        <div className="glass-card mb-4" style={{ padding: '12px', background: 'var(--error)', color: 'white', textAlign: 'center', fontWeight: 600 }}>
                            ⚠️ {error}
                        </div>
                    )}
                    <div className="glass-card mb-4" style={{ padding: '32px', textAlign: 'center' }}>
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            <div style={{ fontSize: '14px', color: 'var(--gray-text)', fontWeight: 600, textTransform: 'uppercase' }}>Current Score</div>
                            <button onClick={handleEditScore} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '12px' }}>✎ Edit</button>
                            <button onClick={handleRefreshScore} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '12px' }}>↺ Refresh</button>
                            <button onClick={toggleScorecard} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '12px', fontWeight: 700 }}>📊 Scorecard</button>
                        </div>
                        <h1 style={{ fontSize: '72px', color: 'var(--primary-blue)', margin: '12px 0' }}>
                            {scoreData.runs}/{scoreData.wickets}
                        </h1>
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', fontSize: '18px', fontWeight: 600 }}>
                            <span style={{ color: 'var(--text-muted)' }}>{scoreData.overs} Overs</span>
                            <span style={{ color: 'var(--primary-blue)' }}>CRR: {Number(scoreData.crr || 0).toFixed(2)}</span>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                        <div className="glass-card" style={{ padding: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ fontSize: '12px', color: 'var(--gray-text)', fontWeight: 700 }}>BATTING</div>
                                <button onClick={handleSwapStrikers} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--primary-blue)', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>⇅ Swap</button>
                            </div>
                            <div className="player-row" style={{ borderBottom: '1px solid var(--slate-100)', paddingBottom: '8px', marginBottom: '8px' }}>
                                <div className="player-name">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase' }}>Striker</div>
                                        <button onClick={() => setShowSelection({ active: true, role: 'striker', team: scoreData.battingTeam })} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '11px' }}>✎ Change</button>
                                    </div>
                                    <div style={{ fontSize: '16px', fontWeight: 700 }}>
                                        {scoreData.strikerName === 'Not Set' ? 'Striker Not Selected' : (scoreData.strikerName || 'Striker')}
                                        {scoreData.strikerName !== 'Not Set' && <span style={{ color: 'var(--primary-blue)', marginLeft: '4px' }}>*</span>}
                                    </div>
                                </div>
                                {scoreData.strikerName !== 'Not Set' && (
                                    <div style={{ fontWeight: 700 }}>{scoreData.strikerRuns || 0} ({scoreData.strikerBalls || 0})</div>
                                )}
                            </div>
                            <div className="player-row">
                                <div className="player-name">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase' }}>Non-Striker</div>
                                        <button onClick={() => setShowSelection({ active: true, role: 'non_striker', team: scoreData.battingTeam })} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '11px' }}>✎ Change</button>
                                    </div>
                                    <div style={{ fontSize: '16px', fontWeight: 700 }}>
                                        {scoreData.nonStrikerName === 'Not Set' ? 'Non-Striker Not Selected' : (scoreData.nonStrikerName || 'Non-Striker')}
                                    </div>
                                </div>
                                {scoreData.nonStrikerName !== 'Not Set' && (
                                    <div style={{ fontWeight: 700 }}>{scoreData.nonStrikerRuns || 0} ({scoreData.nonStrikerBalls || 0})</div>
                                )}
                            </div>
                            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--slate-100)', display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                                <span style={{ color: 'var(--gray-text)' }}>Partnership</span>
                                <span style={{ fontWeight: 700 }}>{partnership.runs ?? 0} ({partnership.balls ?? 0})</span>
                            </div>
                        </div>

                        <div className="glass-card" style={{ padding: '20px' }}>
                            <div style={{ fontSize: '12px', color: 'var(--gray-text)', fontWeight: 700, marginBottom: '16px' }}>BOWLING</div>
                            <div className="player-row" style={{ border: 'none' }}>
                                <div className="player-name">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Bowler</div>
                                        <button onClick={() => setShowSelection({ active: true, role: 'bowler', team: scoreData.bowlingTeam })} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0', color: 'var(--primary-blue)', fontSize: '12px' }}>✎ Change</button>
                                    </div>
                                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{scoreData.bowlerName === 'Not Set' ? 'Bowler Not Selected' : (scoreData.bowlerName || 'Current Bowler')}</div>
                                </div>
                                {scoreData.bowlerName !== 'Not Set' && (
                                    <div style={{ fontWeight: 700, fontSize: '14px' }}>
                                        Wkts: <span style={{ color: 'var(--primary-blue)' }}>{scoreData.bowlerWickets || 0}</span> |
                                        Runs: <span style={{ color: 'var(--primary-blue)' }}>{scoreData.bowlerRuns || 0}</span>
                                        <span style={{ fontSize: '12px', fontWeight: 400, marginLeft: '8px', color: 'var(--gray-text)' }}>({scoreData.bowlerOvers || "0.0"} ov)</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="glass-card" style={{ padding: '20px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <span style={{ fontWeight: 700 }}>Current Over Timeline</span>
                            <button className="btn-text" onClick={handleUndo} style={{ color: 'var(--error)', fontSize: '12px', padding: 0 }}>Undo Ball</button>
                        </div>
                        <div className="over-timeline" style={{ padding: 0, display: 'flex', gap: '8px' }}>
                            {timeline.length === 0 ? (
                                <div style={{ color: 'var(--gray-text)', fontSize: '13px', fontStyle: 'italic' }}>Waiting for first ball...</div>
                            ) : (
                                timeline.map((b, i) => {
                                    let bg = 'var(--slate-100)';
                                    let color = 'var(--text-main)';
                                    if (b === '4' || b === '6') { bg = 'var(--light-blue)'; color = 'var(--primary-blue)'; }
                                    if (b === 'W') { bg = 'var(--error)'; color = 'white'; }
                                    if (b && String(b).match(/[WdNbBLP]/)) { bg = 'var(--warning)'; color = 'white'; }

                                    return (
                                        <div key={i} style={{
                                            width: '32px', height: '32px', borderRadius: '50%', background: bg, color: color,
                                            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700
                                        }}>
                                            {b}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </div>

                <div className="scoring-actions-col">

                    <div className="glass-card" style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <div style={{ fontWeight: 700, marginBottom: '20px' }}>Input Runs</div>
                        <div className="scoring-grid" style={{ padding: 0, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                            {[0, 1, 2, 3, 4, 6].map(r => (
                                <button key={r} className="btn" style={{
                                    height: '80px', background: 'var(--white)',
                                    color: (r === 4 || r === 6) ? 'var(--primary-blue)' : 'var(--text-main)',
                                    borderColor: 'var(--slate-200)',
                                    fontSize: '24px', fontWeight: 800,
                                    boxShadow: (r === 4 || r === 6) ? '0 4px 12px rgba(0, 122, 255, 0.1)' : 'none'
                                }} onClick={() => handleAction(r)}>
                                    {r}
                                </button>
                            ))}
                        </div>

                        {showExtraMenu ? (
                            <div className="extra-options-grid" style={{
                                marginTop: '16px', padding: '16px', background: 'var(--slate-50)',
                                borderRadius: '12px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px'
                            }}>
                                <div style={{ gridColumn: 'span 4', fontWeight: 600, fontSize: '13px', marginBottom: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ color: 'var(--primary-blue)' }}>{showExtraMenu.replace('_', ' ')} + Runs</span>
                                    <button onClick={() => setShowExtraMenu(null)} style={{ border: 'none', background: 'none', color: 'var(--error)', cursor: 'pointer', fontWeight: 700 }}>×</button>
                                </div>
                                {((showExtraMenu === 'WIDE' || showExtraMenu === 'NO_BALL') ? [0, 1, 2, 3, 4, 6] : [1, 2, 3, 4, 6]).map(r => (
                                    <button key={r} className="btn" style={{ fontSize: '12px', padding: '8px 0', minWidth: 0 }} onClick={() => { handleAction(r, showExtraMenu); setShowExtraMenu(null); }}>
                                        {r}
                                    </button>
                                ))}
                                {(showExtraMenu === 'WIDE' || showExtraMenu === 'NO_BALL') && (
                                    <button className="btn" style={{ fontSize: '12px', padding: '8px 0', background: 'var(--error)', color: 'white', borderColor: 'var(--error)', fontWeight: 700 }}
                                        onClick={() => { handleAction(0, showExtraMenu, true); setShowExtraMenu(null); }}>
                                        WKT
                                    </button>
                                )}
                            </div>
                        ) : (
                            <>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: '24px', marginBottom: '12px' }}>
                                    <button className="btn-text" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)' }} onClick={() => setShowExtraMenu('WIDE')}>WIDE</button>
                                    <button className="btn-text" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)' }} onClick={() => setShowExtraMenu('NO_BALL')}>NO BALL</button>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginTop: '12px' }}>
                                    <button className="btn-text" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }} onClick={() => setShowExtraMenu('BYE')}>BYE</button>
                                    <button className="btn-text" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }} onClick={() => setShowExtraMenu('LEG_BYE')}>LEG-BYE</button>
                                    <button className="btn-text" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }} onClick={() => handleAction(5, "PENALTY")}>PENALTY</button>
                                </div>
                            </>
                        )}


                        <div style={{ margin: '24px 0', borderTop: '1px solid var(--slate-100)', paddingTop: '24px' }}>
                            <button className="btn" style={{ width: '100%', background: 'var(--error)', color: 'white', height: '60px', fontSize: '18px', fontWeight: 700 }} onClick={() => handleAction(0, "NONE", true)}>
                                WICKET
                            </button>
                        </div>

                        <div style={{ flex: 1 }}></div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <button className="btn" onClick={() => navigate('/predictions', {
                                state: {
                                    matchConfig: {
                                        ...config,
                                        teamA: matchDetails.teamA,
                                        teamB: matchDetails.teamB,
                                        striker: scoreData.strikerName,
                                        nonStriker: scoreData.nonStrikerName,
                                        currentInnings: currentInnings
                                    }
                                }
                            })} style={{ borderColor: 'var(--primary-blue)', color: 'var(--primary-blue)' }}>
                                Match Predictor
                            </button>
                            <button className="btn btn-primary" onClick={handleEndInnings} style={{ background: currentInnings === 1 ? 'var(--primary-blue)' : 'var(--error)' }}>
                                {currentInnings === 1 ? 'End Innings' : 'End Match'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {/* Player Selection Modal */}
            {showSelection.active && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center',
                    zIndex: 2000
                }}>
                    <div style={{
                        backgroundColor: 'white', padding: '24px', borderRadius: '12px',
                        width: '90%', maxWidth: '400px', maxHeight: '80vh', overflowY: 'auto'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <h3 style={{ margin: 0 }}>
                                    {showSelection.role === 'wicket_out_selection' ? 'Select Out Batsman' :
                                        showSelection.role === 'wicket_replacement' ? 'Select Next Batsman' : `Select ${showSelection.role.replace('_', ' ')}`}
                                </h3>
                                <div style={{ fontSize: '12px', color: 'var(--primary-blue)', fontWeight: 'bold', marginTop: '4px' }}>
                                    Team: {(showSelection.team || 'Unknown').toUpperCase()}
                                </div>
                            </div>
                            <button onClick={() => { setShowSelection({ active: false, role: '', team: '' }); setManualName(''); setShowAllPlayersToggle(false); }} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
                        </div>

                        {showSelection.role === 'wicket_out_selection' ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px 0' }}>
                                <p style={{ color: 'var(--gray-text)', margin: 0 }}>Which batsman is out?</p>
                                <button className="btn" style={{ padding: '16px', fontWeight: 'bold', borderColor: 'var(--slate-200)', background: 'var(--slate-50)', color: 'var(--text-main)', textAlign: 'left' }}
                                    onClick={() => {
                                        setPendingBall(prev => ({ ...prev, out_batsman: scoreData.strikerName }));
                                        setShowSelection({ ...showSelection, role: 'wicket_replacement' });
                                    }}
                                >
                                    <div style={{ fontSize: '12px', color: 'var(--error)', marginBottom: '4px' }}>Striker</div>
                                    <div style={{ fontSize: '18px' }}>{scoreData.strikerName}</div>
                                </button>
                                <button className="btn" style={{ padding: '16px', fontWeight: 'bold', borderColor: 'var(--slate-200)', background: 'var(--slate-50)', color: 'var(--text-main)', textAlign: 'left' }}
                                    onClick={() => {
                                        setPendingBall(prev => ({ ...prev, out_batsman: scoreData.nonStrikerName }));
                                        setShowSelection({ ...showSelection, role: 'wicket_replacement' });
                                    }}
                                >
                                    <div style={{ fontSize: '12px', color: 'var(--error)', marginBottom: '4px' }}>Non-Striker</div>
                                    <div style={{ fontSize: '18px' }}>{scoreData.nonStrikerName}</div>
                                </button>
                            </div>
                        ) : (
                            <div style={{ paddingTop: '8px' }}>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                        <div style={{ fontSize: '13px', color: 'var(--gray-text)' }}>
                                            {showAllPlayersToggle ? 'Showing All Match Players' : `Showing ${showSelection.team} Players`}
                                        </div>
                                        <button 
                                            onClick={() => setShowAllPlayersToggle(!showAllPlayersToggle)}
                                            style={{ fontSize: '11px', padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'var(--slate-50)', cursor: 'pointer' }}
                                        >
                                            {showAllPlayersToggle ? 'Filter by Team' : 'Show All Teams'}
                                        </button>
                                    </div>

                                    {allPlayers
                                        .filter(p => showAllPlayersToggle || (p.team_name || '').trim().toLowerCase() === (showSelection.team || '').trim().toLowerCase())
                                        .filter(p => !outPlayers.includes(p.player_name))
                                        .filter(p => p.player_name !== scoreData.strikerName && p.player_name !== scoreData.nonStrikerName)
                                        .filter(p => showSelection.role !== 'bowler' || (p.player_name || '').trim().toLowerCase() !== (scoreData.lastBowler || '').trim().toLowerCase())
                                        .map(playerEntry => (
                                            <button key={playerEntry.player_name} className="btn" onClick={() => handlePlayerChange(playerEntry.player_name)} style={{
                                                textAlign: 'left', padding: '12px', borderColor: 'var(--border-color)',
                                                background: 'white', display: 'flex', justifyContent: 'space-between'
                                            }}>
                                                <span>{playerEntry.player_name}</span>
                                                {showAllPlayersToggle && <span style={{ fontSize: '10px', color: 'var(--gray-text)' }}>{playerEntry.team_name}</span>}
                                            </button>
                                        ))}
                                    {allPlayers.filter(p => (p.team_name || '').trim().toLowerCase() === (showSelection.team || '').trim().toLowerCase()).length === 0 && (
                                        <>
                                            <div style={{ textAlign: 'center', color: 'var(--gray-text)', padding: '20px' }}>
                                                No players found for team "{showSelection.team}".
                                                (All {allPlayers.length} matches players loaded)
                                            </div>
                                            <button className="btn" onClick={() => fetchGlobalPlayers(showSelection.team)} style={{ fontSize: '12px', padding: '8px', background: 'var(--light-blue)', color: 'var(--primary-blue)', borderColor: 'var(--primary-blue)' }}>
                                                🔄 Fetch from Team Roster
                                            </button>
                                            <button className="btn" onClick={fetchInitialData} style={{ fontSize: '12px', padding: '8px', marginTop: '8px' }}>
                                                🔄 Sync Match Players
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Edit Score Modal */}
            {editScoreModal.active && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center',
                    zIndex: 2000
                }}>
                    <div style={{
                        backgroundColor: 'white', padding: '24px', borderRadius: '12px',
                        width: '90%', maxWidth: '300px'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h3 style={{ margin: 0 }}>Edit Score</h3>
                            <button onClick={() => setEditScoreModal({ ...editScoreModal, active: false })} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <div>
                                <label style={{ fontSize: '12px', color: 'var(--gray-text)' }}>Runs</label>
                                <input
                                    type="number"
                                    value={editScoreModal.runs}
                                    onChange={(e) => setEditScoreModal({ ...editScoreModal, runs: parseInt(e.target.value) || 0 })}
                                    style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--slate-200)', marginTop: '4px' }}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '12px', color: 'var(--gray-text)' }}>Wickets</label>
                                <input
                                    type="number"
                                    value={editScoreModal.wickets}
                                    onChange={(e) => setEditScoreModal({ ...editScoreModal, wickets: parseInt(e.target.value) || 0 })}
                                    style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--slate-200)', marginTop: '4px' }}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '12px', color: 'var(--gray-text)' }}>Overs (e.g. 1.2)</label>
                                <input
                                    type="text"
                                    value={editScoreModal.overs}
                                    onChange={(e) => setEditScoreModal({ ...editScoreModal, overs: e.target.value })}
                                    style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--slate-200)', marginTop: '4px' }}
                                />
                            </div>
                            <button className="btn btn-primary" onClick={saveEditedScore} style={{ marginTop: '12px', background: 'var(--primary-blue)' }}>
                                Save Score
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Scorecard Modal */}
            {showScorecard && scorecardData && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center',
                    zIndex: 2000, overflowY: 'auto', padding: '20px'
                }}>
                    <div className="glass-card" style={{
                        backgroundColor: 'white', padding: '24px', borderRadius: '12px',
                        width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto',
                        position: 'relative', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                            <h2 style={{ margin: 0, color: 'var(--primary-blue)', fontSize: '24px', fontWeight: 800 }}>Full Scorecard</h2>
                            <button onClick={() => setShowScorecard(false)} style={{ background: 'none', border: 'none', fontSize: '28px', cursor: 'pointer', color: 'var(--gray-text)' }}>×</button>
                        </div>

                        <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', background: 'var(--slate-100)', padding: '4px', borderRadius: '12px' }}>
                            <button 
                                onClick={() => setScorecardTeamId('team_a')}
                                style={{
                                    flex: 1, padding: '12px', border: 'none', borderRadius: '8px',
                                    background: scorecardTeamId === 'team_a' ? 'white' : 'transparent',
                                    fontWeight: 700, cursor: 'pointer',
                                    boxShadow: scorecardTeamId === 'team_a' ? '0 4px 6px -1px rgba(0,0,0,0.1)' : 'none',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {matchDetails.teamA}
                            </button>
                            <button 
                                onClick={() => setScorecardTeamId('team_b')}
                                style={{
                                    flex: 1, padding: '12px', border: 'none', borderRadius: '8px',
                                    background: scorecardTeamId === 'team_b' ? 'white' : 'transparent',
                                    fontWeight: 700, cursor: 'pointer',
                                    boxShadow: scorecardTeamId === 'team_b' ? '0 4px 6px -1px rgba(0,0,0,0.1)' : 'none',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {matchDetails.teamB}
                            </button>
                        </div>

                        <div className="scorecard-section">
                            <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-blue)', marginBottom: '12px', borderLeft: '4px solid var(--primary-blue)', paddingLeft: '12px' }}>Batting</h3>
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'separate', borderSpacing: '0 8px' }}>
                                    <thead>
                                        <tr style={{ background: 'var(--slate-50)', color: 'var(--gray-text)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                            <th style={{ padding: '12px' }}>Batsman</th>
                                            <th style={{ padding: '12px' }}>Status</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>R</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>B</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>4s</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>6s</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>SR</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {scorecardData[scorecardTeamId].batting.map((b, i) => (
                                            <tr key={i} style={{ background: 'var(--white)', borderBottom: '1px solid var(--slate-100)' }}>
                                                <td style={{ padding: '12px', fontWeight: 700, color: 'var(--text-main)' }}>{b.player_name}</td>
                                                <td style={{ padding: '12px', fontSize: '12px', color: 'var(--gray-text)' }}>{b.status}</td>
                                                <td style={{ padding: '12px', textAlign: 'right', fontWeight: 800, color: 'var(--primary-blue)' }}>{b.runs}</td>
                                                <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-muted)' }}>{b.balls}</td>
                                                <td style={{ padding: '12px', textAlign: 'right' }}>{b.fours}</td>
                                                <td style={{ padding: '12px', textAlign: 'right' }}>{b.sixes}</td>
                                                <td style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: 'var(--gray-text)' }}>
                                                    {b.balls > 0 ? ((b.runs / b.balls) * 100).toFixed(1) : '0.0'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="scorecard-section" style={{ marginTop: '32px' }}>
                            <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-blue)', marginBottom: '12px', borderLeft: '4px solid var(--primary-blue)', paddingLeft: '12px' }}>Bowling</h3>
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'separate', borderSpacing: '0 8px' }}>
                                    <thead>
                                        <tr style={{ background: 'var(--slate-50)', color: 'var(--gray-text)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                            <th style={{ padding: '12px' }}>Bowler</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>O</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>M</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>R</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>W</th>
                                            <th style={{ padding: '12px', textAlign: 'right' }}>Econ</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {scorecardData[scorecardTeamId].bowling.map((bo, i) => {
                                            const overs = parseFloat(bo.overs) || 0;
                                            return (
                                                <tr key={i} style={{ background: 'var(--white)' }}>
                                                    <td style={{ padding: '12px', fontWeight: 700, color: 'var(--text-main)' }}>{bo.player_name}</td>
                                                    <td style={{ padding: '12px', textAlign: 'right' }}>{bo.overs}</td>
                                                    <td style={{ padding: '12px', textAlign: 'right' }}>{bo.maidens}</td>
                                                    <td style={{ padding: '12px', textAlign: 'right' }}>{bo.runs}</td>
                                                    <td style={{ padding: '12px', textAlign: 'right', fontWeight: 800, color: 'var(--primary-blue)' }}>{bo.wickets}</td>
                                                    <td style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: 'var(--gray-text)' }}>
                                                        {overs > 0 ? (bo.runs / overs).toFixed(2) : '0.00'}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                        {scorecardData[scorecardTeamId].bowling.length === 0 && (
                                            <tr>
                                                <td colSpan="6" style={{ padding: '24px', textAlign: 'center', color: 'var(--gray-text)', fontStyle: 'italic' }}>No bowling stats yet</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div style={{ marginTop: '24px', textAlign: 'center' }}>
                            <button onClick={() => setShowScorecard(false)} className="btn btn-primary" style={{ padding: '10px 32px' }}>Close Scorecard</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Scoring;
