const API_BASE_URL = 'http://127.0.0.1:5005';

class ApiService {
    static async _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static async request(endpoint, options = {}, retryCount = 0) {
        const MAX_RETRIES = 3;
        const INITIAL_BACKOFF = 1000; // 1 second
        const url = `${API_BASE_URL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const text = await response.text();
            // Reduced logging for production-like feel, but keeping it during debug
            if (process.env.NODE_ENV === 'development') {
                console.log(`API DEBUG [${endpoint}]:`, text.substring(0, 100));
            }

            let data = {};
            try {
                data = text ? JSON.parse(text) : {};
            } catch (jsonError) {
                console.error("JSON PARSE ERROR:", jsonError, "FOR TEXT:", text);
                data = { message: text || `Response error (${response.status}): Could not parse JSON` };
            }

            if (!response.ok) {
                const error = new Error(data.message || data.error || `API ERROR ${response.status}`);
                error.status = response.status;
                error.data = data;
                throw error;
            }
            
            return data;
        } catch (error) {
            // If it's a known API error with status, don't retry (e.g. 404, 401, 500)
            if (error.status) throw error;
            
            // Check if it's a network/TypeError (backend down, CORS, etc.)
            const isNetworkError = error.name === 'TypeError' || error.message.includes('fetch');
            
            if (isNetworkError && retryCount < MAX_RETRIES) {
                const backoff = INITIAL_BACKOFF * Math.pow(2, retryCount);
                console.warn(`Network failure on ${endpoint}. Retrying in ${backoff}ms... (Attempt ${retryCount + 1}/${MAX_RETRIES})`);
                await this._sleep(backoff);
                return this.request(endpoint, options, retryCount + 1);
            }

            console.error("Final fetch failure:", error);
            
            if (isNetworkError) {
               throw new Error("Network error: Backend unreachable or CORS issue. We tried 3 times to reconnect.");
            }
            
            throw error;
        }
    }
}

export default ApiService;
