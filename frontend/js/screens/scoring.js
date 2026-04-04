import appRouter from '../router.js';
import ApiService from '../api.js';

let overTimeline = [];

appRouter.registerScreen('scoring', 'scoring-screen', () => {
    if (!window.activeMatchConfig) {
        appRouter.navigate('home');
        return;
    }
    
    // Initial UI Population
    document.getElementById('score-match-title').innerText = `${window.activeMatchConfig.teamA} vs ${window.activeMatchConfig.teamB}`;
    
    document.getElementById('score-striker-name').innerHTML = `${window.activeMatchConfig.striker} <span class="striker-indicator" id="striker-star">*</span>`;
    document.getElementById('score-non-striker-name').innerHTML = `${window.activeMatchConfig.nonStriker} <span class="striker-indicator" id="non-striker-star" style="display:none;">*</span>`;
    document.getElementById('score-bowler-name').innerText = window.activeMatchConfig.bowler;
    
    overTimeline = [];
    refreshScoreData();
});

document.getElementById('btn-score-back').addEventListener('click', () => appRouter.navigate('home'));

document.getElementById('btn-go-predictions').addEventListener('click', () => appRouter.navigate('predictions'));

document.querySelectorAll('.runs-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
        const runs = parseInt(e.currentTarget.getAttribute('data-runs') || 0);
        const extrasType = e.currentTarget.getAttribute('data-extras'); // 1=W, 2=NB, null=none
        
        let displayBubble = runs.toString();
        if (extrasType === '1') displayBubble = 'Wd';
        if (extrasType === '2') displayBubble = 'Nb';
        
        const payload = {
            match_id: window.activeMatchConfig.id,
            runs: runs,
            extras_type: extrasType ? parseInt(extrasType) : null
        };
        
        addTimelineBubble(displayBubble);
        await updateScoreAction(payload);
    });
});

document.getElementById('btn-wicket').addEventListener('click', async () => {
    // In a real app we'd prompt for wicket type, let's keep it simple
    addTimelineBubble('W');
    await updateScoreAction({
        match_id: window.activeMatchConfig.id,
        is_wicket: true
    });
});

document.getElementById('btn-end-innings').addEventListener('click', () => {
    appRouter.showToast('Innings ended. (Stub)');
});

function addTimelineBubble(val) {
    overTimeline.push(val);
    renderTimeline();
}

function renderTimeline() {
    const container = document.getElementById('score-over-timeline');
    container.innerHTML = '';
    overTimeline.forEach(b => {
        let cls = 'ball-bubble';
        if (b === '4') cls += ' boundary';
        if (b === '6') cls += ' six';
        if (b === 'W') cls += ' wicket';
        container.innerHTML += `<div class="${cls}">${b}</div>`;
    });
}

async function updateScoreAction(payload) {
    try {
        await ApiService.request('/match/update', { method: 'POST', body: JSON.stringify(payload) });
        refreshScoreData();
    } catch (e) {
        appRouter.showToast(e.message, 'error');
    }
}

async function refreshScoreData() {
    if (!window.activeMatchConfig) return;
    try {
        const d = await ApiService.request(`/match/score?match_id=${window.activeMatchConfig.id}`);
        
        document.getElementById('score-main-runs').innerText = `${d.runs}/${d.wickets}`;
        document.getElementById('score-main-overs').innerText = `(${d.overs.toFixed(1)} Overs)`;
        document.getElementById('score-crr').innerText = d.crr.toFixed(2);
        
        // Mock individual player stats update for visualization
        // In reality, backend should return individual maps
        document.getElementById('score-striker-runs').innerText = d.runs > 0 ? Math.floor(d.runs * 0.6) : 0;
        document.getElementById('score-striker-balls').innerText = `(${Math.floor(d.overs * 6 * 0.6)})`;
        
        document.getElementById('score-non-striker-runs').innerText = d.runs > 0 ? Math.floor(d.runs * 0.4) : 0;
        document.getElementById('score-non-striker-balls').innerText = `(${Math.floor(d.overs * 6 * 0.4)})`;
        
        document.getElementById('score-bowler-figures').innerText = `${d.wickets}-${d.runs}`;
        document.getElementById('score-bowler-overs').innerText = `(${d.overs.toFixed(1)})`;

        // Manage timeline length
        if (d.balls_in_over === 0 && overTimeline.length >= 6) {
           setTimeout(() => { overTimeline = []; renderTimeline(); }, 2000);
        }

    } catch (e) {
        console.error("Score refresh error:", e);
    }
}
