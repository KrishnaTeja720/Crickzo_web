import appRouter from './router.js';
import ApiService from './api.js';
import './screens/home.js';
import './screens/create_match.js';
import './screens/scoring.js';
import './screens/predictions.js';

// Application State
const state = {
    userEmail: localStorage.getItem('user_email') || '',
    userName: localStorage.getItem('user_name') || '',
    userId: localStorage.getItem('user_id') || 0,
    otpSubtitle: 'Complete Your Registration'
};

function saveUser(id, name, email) {
    state.userId = id;
    state.userName = name;
    state.userEmail = email;
    localStorage.setItem('user_id', id);
    localStorage.setItem('user_name', name);
    localStorage.setItem('user_email', email);
}

function clearUser() {
    state.userId = 0;
    state.userName = '';
    state.userEmail = '';
    localStorage.clear();
}

// ============================================
// SCREENS REGISTRATION
// ============================================

appRouter.registerScreen('splash', 'splash-screen', () => {
    // Simulate Splash screen delay like Android
    setTimeout(() => {
        if (state.userEmail && state.userId) {
            appRouter.navigate('home');
        } else {
            appRouter.navigate('login');
        }
    }, 2000);
});

appRouter.registerScreen('login', 'login-screen');
appRouter.registerScreen('signup', 'signup-screen');
appRouter.registerScreen('forgot_password', 'forgot-pw-screen');
appRouter.registerScreen('verify_otp', 'verify-otp-screen', () => {
    document.getElementById('otp-subtitle').innerText = state.otpSubtitle;
    document.getElementById('otp-email-display').innerText = state.userEmail;
});
appRouter.registerScreen('reset_password', 'reset-pw-screen');

// Dummy Home Screen placeholder for now
appRouter.registerScreen('home', 'home-screen');

// ============================================
// EVENT LISTENERS: LOGIN
// ============================================

document.getElementById('btn-go-signup').addEventListener('click', () => {
    appRouter.navigate('signup');
});

document.getElementById('btn-forgot-password').addEventListener('click', () => {
    appRouter.navigate('forgot_password');
});

document.getElementById('btn-login').addEventListener('click', async () => {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        appRouter.showToast('Please fill all fields', 'error');
        return;
    }

    const btn = document.getElementById('btn-login');
    btn.disabled = true;
    btn.innerText = 'Signing In...';

    try {
        const res = await ApiService.login({ email, password });
        if (res.status === 'success') {
            saveUser(res.user_id, res.name, email);
            appRouter.showToast(`Welcome back, ${res.name}!`);
            appRouter.navigate('home');
        } else {
            appRouter.showToast('Invalid credentials', 'error');
        }
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Sign In';
    }
});

// ============================================
// EVENT LISTENERS: SIGNUP
// ============================================

document.getElementById('btn-signup-back').addEventListener('click', () => {
    appRouter.goBack();
});

document.getElementById('btn-signup').addEventListener('click', async () => {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    if (!name || !email || !password) {
        appRouter.showToast('Please fill all fields', 'error');
        return;
    }

    const btn = document.getElementById('btn-signup');
    btn.disabled = true;
    btn.innerText = 'Registering...';

    try {
        const res = await ApiService.signup({ name, email, password });
        if (res.status === 'success') {
            state.userEmail = email;
            state.userName = name;
            state.otpSubtitle = "Complete Your Registration";
            
            // Trigger OTP Generation matching Android `coroutineScope.launch` behavior
            ApiService.resendOtp({ email }).catch(e => console.error("OTP generation silent fail:", e));
            
            appRouter.navigate('verify_otp');
        } else {
             appRouter.showToast(res.message, 'error');
        }
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Register';
    }
});

// ============================================
// EVENT LISTENERS: VERIFY OTP
// ============================================
document.getElementById('btn-otp-back').addEventListener('click', () => {
    appRouter.goBack();
});

document.getElementById('btn-verify-otp').addEventListener('click', async () => {
    const otp = document.getElementById('verify-otp-code').value;
    
    if (otp.length !== 6) {
        appRouter.showToast('Please enter a valid 6-digit OTP', 'error');
        return;
    }

    const btn = document.getElementById('btn-verify-otp');
    btn.disabled = true;

    try {
        const res = await ApiService.verifyOtp({ email: state.userEmail, otp });
        if (res.status === 'verified') {
            if (state.otpSubtitle === 'Verify Your Identity') {
                 appRouter.navigate('reset_password');
            } else {
                 appRouter.showToast('Account successfully verified. Please login.');
                 appRouter.navigate('login');
            }
        } else {
            appRouter.showToast('Invalid OTP', 'error');
        }
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('btn-resend-otp').addEventListener('click', async () => {
    try {
        await ApiService.resendOtp({ email: state.userEmail });
        appRouter.showToast('OTP Resent successfully');
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    }
});

// ============================================
// EVENT LISTENERS: FORGOT/RESET PASSWORD
// ============================================
document.getElementById('btn-forgot-pw-back').addEventListener('click', () => {
    appRouter.goBack();
});

document.getElementById('btn-send-reset-otp').addEventListener('click', async () => {
    const email = document.getElementById('forgot-pw-email').value;
    if (!email) {
        appRouter.showToast('Please enter your email', 'error');
        return;
    }

    const btn = document.getElementById('btn-send-reset-otp');
    btn.disabled = true;
    
    try {
        await ApiService.forgotPassword({ email });
        state.userEmail = email;
        state.otpSubtitle = "Verify Your Identity";
        appRouter.navigate('verify_otp');
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('btn-reset-password').addEventListener('click', async () => {
    const new_password = document.getElementById('reset-new-password').value;
    if (!new_password) {
        appRouter.showToast('Please enter a new password', 'error');
        return;
    }

    const btn = document.getElementById('btn-reset-password');
    btn.disabled = true;

    try {
        await ApiService.resetPassword({ email: state.userEmail, new_password });
        appRouter.showToast('Password updated successfully. Please login.');
        appRouter.navigate('login');
    } catch (err) {
        appRouter.showToast(err.message, 'error');
    } finally {
        btn.disabled = false;
    }
});


// Initialization
document.addEventListener('DOMContentLoaded', () => {
    appRouter.navigate('splash');
});

// Export functions if needed by other modules
export { saveUser, clearUser, state };
