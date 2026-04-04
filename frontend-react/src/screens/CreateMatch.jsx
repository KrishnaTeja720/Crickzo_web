import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const CreateMatch = () => {
    const [teamA, setTeamA] = useState('');
    const [teamB, setTeamB] = useState('');
    const [format, setFormat] = useState('20');
    const [venue, setVenue] = useState('');
    const [toss, setToss] = useState('Team A');
    const [tossDecision, setTossDecision] = useState('Batting');
    const [pitch, setPitch] = useState('Batting');
    const [weather, setWeather] = useState('Clear');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const showToast = useToast();

    const handleCreateMatch = async () => {
        const userId = user?.userId || JSON.parse(localStorage.getItem('user'))?.userId;
        
        if (!userId) {
            showToast('User session expired. Please log in again.', 'error');
            navigate('/login');
            return;
        }

        if (!teamA || !teamB) {
            showToast('Team names cannot be empty', 'error');
            return;
        }

        const nameRegex = /^[A-Za-z\s]+$/;
        if (!nameRegex.test(teamA) || !nameRegex.test(teamB)) {
            showToast('Team names must only contain alphabetical characters', 'warning');
            return;
        }

        setLoading(true);

        try {
            const payload = {
                user_id: userId,
                team_a: teamA,
                team_b: teamB,
                format,
                venue,
                toss,
                toss_decision: tossDecision,
                pitch,
                weather
            };

            const res = await ApiService.request('/match/create', { 
                method: 'POST', 
                body: JSON.stringify(payload) 
            });
            
            if (res.status === 'success') {
                const config = {
                    id: res.match_id,
                    teamA,
                    teamB,
                    tossWinner: toss,
                    tossDecision: tossDecision,
                    playersA: [],
                    playersB: []
                };
                navigate(`/setup_match/${res.match_id}`, { state: { matchConfig: config } });
            } else {
                showToast(res.error || 'Failed to create match', 'error');
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
                <button className="btn-text" onClick={() => navigate(-1)} style={{ padding: 0 }}>&larr; Back</button>
                <div className="section-title">New Match</div>
                <div style={{ width: '40px' }}></div>
            </div>
            
            <div className="form-group mt-4">
                <label>Team A Name</label>
                <input type="text" value={teamA} onChange={e => setTeamA(e.target.value)} className="input-field" placeholder="E.g., Mumbai Indians" />
            </div>
            <div className="form-group">
                <label>Team B Name</label>
                <input type="text" value={teamB} onChange={e => setTeamB(e.target.value)} className="input-field" placeholder="E.g., Chennai Super Kings" />
            </div>
            <div className="form-group">
                <label>Number of Overs</label>
                <input 
                    type="number" 
                    value={format} 
                    onChange={e => setFormat(e.target.value)} 
                    className="input-field" 
                    placeholder="E.g., 20"
                    min="1"
                    max="100"
                />
            </div>
            <div className="form-group">
                <label>Venue (Optional)</label>
                <input type="text" value={venue} onChange={e => setVenue(e.target.value)} className="input-field" placeholder="Location" />
            </div>
            <div className="form-group">
                <label>Toss Won By</label>
                <select value={toss} onChange={e => setToss(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="Team A">Team A</option>
                    <option value="Team B">Team B</option>
                </select>
            </div>
            <div className="form-group">
                <label>Toss Decision</label>
                <select value={tossDecision} onChange={e => setTossDecision(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="Batting">Batting First</option>
                    <option value="Bowling">Bowling First</option>
                </select>
            </div>
            <div className="form-group">
                <label>Pitch Type</label>
                <select value={pitch} onChange={e => setPitch(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="Batting">Batting</option>
                    <option value="Bowling">Bowling</option>
                    <option value="Balanced">Balanced</option>
                </select>
            </div>
            <div className="form-group mb-4">
                <label>Weather conditions</label>
                <select value={weather} onChange={e => setWeather(e.target.value)} className="input-field" style={{ backgroundColor: 'white' }}>
                    <option value="Clear">Clear</option>
                    <option value="Cloudy">Cloudy</option>
                    <option value="Overcast">Overcast</option>
                </select>
            </div>
            
            <button className="btn btn-primary mt-4" onClick={handleCreateMatch} disabled={loading}>
                {loading ? 'Creating...' : 'Continue'}
            </button>
        </div>
    );
};

export default CreateMatch;
