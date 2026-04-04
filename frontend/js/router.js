class Router {
    constructor() {
        this.currentScreen = null;
        this.history = [];
        this.screens = {};
        
        // Setup Toast Container
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
    }

    registerScreen(name, elementId, onEnter = null, onLeave = null) {
        this.screens[name] = {
            element: document.getElementById(elementId),
            onEnter,
            onLeave
        };
    }

    navigate(screenName, replace = false) {
        if (!this.screens[screenName]) {
            console.error(`Screen ${screenName} not found`);
            return;
        }

        if (this.currentScreen) {
            const current = this.screens[this.currentScreen];
            current.element.classList.remove('active');
            if (current.onLeave) current.onLeave();
            
            if (!replace) {
                this.history.push(this.currentScreen);
            }
        }

        this.currentScreen = screenName;
        const next = this.screens[screenName];
        next.element.classList.add('active');
        if (next.onEnter) next.onEnter();
    }

    goBack() {
        if (this.history.length > 0) {
            const previousScreen = this.history.pop();
            this.navigate(previousScreen, true);
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeIn 0.3s ease-in reverse forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

const appRouter = new Router();
export default appRouter;
