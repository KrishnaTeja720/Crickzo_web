import appRouter from './router.js';
import ApiService from './api.js';
import { clearUser, state } from './app.js';

appRouter.registerScreen('home', 'home-screen', async () => {
    document.getElementById('home-user-name').innerText = state.userName;

    try {
        const liveMatches = await ApiService.request(`/matches/live?user_id=${state.userId}`);
        const container = document.getElementById('home-live-matches-container');
        
        // Use user's ID to fetch created matches count (approximation)
        // Usually would fetch completed matches length + live matches length
        document.getElementById('home-created-count').innerText = `${liveMatches.length} matches`;

        if (liveMatches.length === 0) {
            container.innerHTML = `<div class="card-empty">No live matches at the moment</div>`;
        } else {
            let html = '<div style="display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px;">';
            liveMatches.slice(0, 2).forEach(match => {
                html += `
                    <div style="flex: 1; min-width: 150px; border: 1px solid #e2e8f0; border-radius: 16px; padding: 12px; background: white;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="width: 8px; height: 8px; border-radius: 50%; background: red; margin-right: 6px;"></div>
                            <span style="color: red; font-size: 10px; font-weight: bold;">LIVE</span>
                        </div>
                        <div style="font-size: 12px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            ${match.teamA || 'Team A'} vs ${match.teamB || 'Team B'}
                        </div>
                        <div style="font-size: 18px; font-weight: 800; color: #1E40AF; margin-top: 4px;">
                            ${match.runs || 0}/${match.wickets || 0}
                        </div>
                        <div style="font-size: 10px; color: #6B7280;">${match.overs || 0} Overs</div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
    } catch (e) {
        console.error("Failed to load live matches:", e);
    }
});

appRouter.registerScreen('profile', 'profile-screen', () => {
    document.getElementById('profile-name').innerText = state.userName;
    document.getElementById('profile-email').innerText = state.userEmail;
    
    // Create Avatar Initials
    const initials = state.userName.length >= 2 ? state.userName.substring(0, 2).toUpperCase() : 'CF';
    document.getElementById('profile-avatar-text').innerText = initials;
});

// Common Bottom Navigation Handlers
const navigateTo = (screen) => appRouter.navigate(screen);

['nav-home', 'nav-home-p'].forEach(id => {
    document.getElementById(id)?.addEventListener('click', () => navigateTo('home'));
});
['nav-add', 'nav-add-p'].forEach(id => {
    document.getElementById(id)?.addEventListener('click', () => navigateTo('create_match'));
});
['nav-profile', 'nav-profile-p', 'btn-home-profile'].forEach(id => {
    document.getElementById(id)?.addEventListener('click', () => navigateTo('profile'));
});

// Profile Actions
document.getElementById('btn-profile-logout').addEventListener('click', () => {
    clearUser();
    appRouter.navigate('login');
});

// Mock hooks to unimplemented screens
document.getElementById('btn-profile-settings').addEventListener('click', () => appRouter.showToast('Account settings coming soon.'));
document.getElementById('btn-action-new-match').addEventListener('click', () => navigateTo('create_match'));
document.getElementById('btn-action-my-matches').addEventListener('click', () => appRouter.showToast('My Matches list coming soon.'));
document.getElementById('btn-action-completed').addEventListener('click', () => appRouter.showToast('Completed Matches coming soon.'));
