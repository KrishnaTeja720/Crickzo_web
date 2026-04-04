import appRouter from '../router.js';
import ApiService from '../api.js';
import { state } from '../app.js';

let currentMatchConfig = {
    id: null,
    teamA: '',
    teamB: '',
    playersA: [],
    playersB: []
};

// ===================================
// CREATE MATCH SCREEN
// ===================================

appRouter.registerScreen('create_match', 'create-match-screen', () => {
    document.getElementById('match-team-a').value = '';
    document.getElementById('match-team-b').value = '';
    document.getElementById('match-venue').value = '';
});

document.getElementById('btn-create-back').addEventListener('click', () => appRouter.goBack());

document.getElementById('btn-create-match').addEventListener('click', async () => {
    const teamA = document.getElementById('match-team-a').value;
    const teamB = document.getElementById('match-team-b').value;
    const format = document.getElementById('match-format').value;
    const venue = document.getElementById('match-venue').value;
    const toss = document.getElementById('match-toss').value;
    const pitch = document.getElementById('match-pitch').value;
    const weather = document.getElementById('match-weather').value;
    
    // Quick validation matching Android
    if (!teamA || !teamB) {
        appRouter.showToast('Team names cannot be empty', 'error');
        return;
    }

    const btn = document.getElementById('btn-create-match');
    btn.disabled = true;
    btn.innerText = 'Creating...';

    try {
        const payload = {
            user_id: parseInt(state.userId),
            team_a: teamA,
            team_b: teamB,
            format: format,
            venue: venue,
            toss: toss,
            pitch: pitch,
            weather: weather
        };

        const res = await ApiService.request('/match/create', { method: 'POST', body: JSON.stringify(payload) });
        
        if (res.status === 'success') {
            currentMatchConfig.id = res.match_id;
            currentMatchConfig.teamA = teamA;
            currentMatchConfig.teamB = teamB;
            currentMatchConfig.playersA = [];
            currentMatchConfig.playersB = [];
            
            appRouter.navigate('setup_match');
        } else {
            appRouter.showToast(res.error || 'Failed to create match', 'error');
        }
    } catch (e) {
        appRouter.showToast(e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Continue';
    }
});

// ===================================
// ADD PLAYERS & SETUP SCREEN
// ===================================

appRouter.registerScreen('setup_match', 'setup-match-screen', () => {
    document.getElementById('setup-team-a-title').innerText = currentMatchConfig.teamA;
    document.getElementById('setup-team-b-title').innerText = currentMatchConfig.teamB;
    updatePlayerLists();
    updateTossSelectors();
});

document.getElementById('btn-setup-back').addEventListener('click', () => {
    appRouter.showToast("Cannot go back. Match ID generated.", "error"); // Android mirrors standard flow usually
});

function updatePlayerLists() {
    // Render Team A
    const listA = document.getElementById('list-team-a');
    listA.innerHTML = '';
    currentMatchConfig.playersA.forEach((p, idx) => {
        listA.innerHTML += `<div class="team-chip" style="margin-right: 4px;">👤 ${p} <span style="margin-left:8px;cursor:pointer;" onclick="window.removePlayer('A', ${idx})">❌</span></div>`;
    });

    // Render Team B
    const listB = document.getElementById('list-team-b');
    listB.innerHTML = '';
    currentMatchConfig.playersB.forEach((p, idx) => {
        listB.innerHTML += `<div class="team-chip" style="margin-right: 4px;">👤 ${p} <span style="margin-left:8px;cursor:pointer;" onclick="window.removePlayer('B', ${idx})">❌</span></div>`;
    });
}

window.removePlayer = (team, idx) => {
    if (team === 'A') currentMatchConfig.playersA.splice(idx, 1);
    else currentMatchConfig.playersB.splice(idx, 1);
    updatePlayerLists();
    updateTossSelectors();
};

document.getElementById('btn-add-player-a').addEventListener('click', () => {
    const input = document.getElementById('input-player-a');
    if (input.value.trim()) {
        currentMatchConfig.playersA.push(input.value.trim());
        input.value = '';
        updatePlayerLists();
        updateTossSelectors();
    }
});

document.getElementById('btn-add-player-b').addEventListener('click', () => {
    const input = document.getElementById('input-player-b');
    if (input.value.trim()) {
        currentMatchConfig.playersB.push(input.value.trim());
        input.value = '';
        updatePlayerLists();
        updateTossSelectors();
    }
});

function updateTossSelectors() {
    // Populate select boxes based on the current arrays
    const strikerSel = document.getElementById('setup-striker');
    const nonStrikerSel = document.getElementById('setup-non-striker');
    const bowlerSel = document.getElementById('setup-bowler');

    strikerSel.innerHTML = '<option value="">Select Striker from Team A</option>';
    nonStrikerSel.innerHTML = '<option value="">Select Non-Striker from Team A</option>';
    bowlerSel.innerHTML = '<option value="">Select Bowler from Team B</option>';

    currentMatchConfig.playersA.forEach(p => {
        strikerSel.innerHTML += `<option value="${p}">${p}</option>`;
        nonStrikerSel.innerHTML += `<option value="${p}">${p}</option>`;
    });

    currentMatchConfig.playersB.forEach(p => {
        bowlerSel.innerHTML += `<option value="${p}">${p}</option>`;
    });
}

document.getElementById('btn-start-match').addEventListener('click', async () => {
    const striker = document.getElementById('setup-striker').value;
    const nonStriker = document.getElementById('setup-non-striker').value;
    const bowler = document.getElementById('setup-bowler').value;

    if (!striker || !nonStriker || !bowler) {
        appRouter.showToast('Please select all starting players', 'error');
        return;
    }

    if (striker === nonStriker) {
        appRouter.showToast('Striker and non-striker cannot be the same player', 'error');
        return;
    }

    const btn = document.getElementById('btn-start-match');
    btn.disabled = true;
    
    // The Python API expects 2 route calls sequentially: /match/setup (which is missing in python, we skip to /match/start and assume it sets the match up properly)
    // Wait, the python code actually comment out "add_players", we'll just call python's /match/start

    try {
        const payload = {
            match_id: currentMatchConfig.id,
            striker: striker,
            non_striker: nonStriker,
            bowler: bowler
        };

        const res = await ApiService.request('/match/start', { method: 'POST', body: JSON.stringify(payload) });
        
        if (res.status === 'success') {
            appRouter.showToast('Match Started!');
            // Store configuration for the active score screen
            window.activeMatchConfig = {
                ...currentMatchConfig,
                striker, nonStriker, bowler
            };
            appRouter.navigate('scoring');
        } else {
             appRouter.showToast(res.error || 'Failed to start match', 'error');
        }
    } catch (e) {
        appRouter.showToast(e.message, 'error');
    } finally {
        btn.disabled = false;
    }
});
