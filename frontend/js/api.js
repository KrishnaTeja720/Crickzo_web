// Base API configurations
const BASE_URL = 'http://127.0.0.1:5000';

class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || data.error || 'API Request Failed');
            }
            
            return data;
        } catch (error) {
            console.error(`[API ERROR] Endpoint: ${endpoint}`, error);
            throw error;
        }
    }

    // Auth
    static signup(data) {
        return this.request('/signup', { method: 'POST', body: JSON.stringify(data) });
    }

    static login(data) {
        return this.request('/login', { method: 'POST', body: JSON.stringify(data) });
    }

    static forgotPassword(data) {
        return this.request('/forgot_password', { method: 'POST', body: JSON.stringify(data) });
    }

    static verifyOtp(data) {
        return this.request('/verify_otp', { method: 'POST', body: JSON.stringify(data) });
    }

    static resetPassword(data) {
        return this.request('/reset_password', { method: 'POST', body: JSON.stringify(data) });
    }

    static resendOtp(data) {
        return this.request('/resend_otp', { method: 'POST', body: JSON.stringify(data) });
    }
}

export default ApiService;
