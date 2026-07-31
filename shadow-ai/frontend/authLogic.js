// Continuation of app logic for Shadow AI

let isLoginMode = true;

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const emailGroup = document.getElementById('emailGroup');
    const authBtn = document.getElementById('authBtn');
    const authToggleText = document.getElementById('authToggleText');
    const subtitle = document.getElementById('authSubtitle');

    if (isLoginMode) {
        if (emailGroup) emailGroup.style.display = 'none';
        const emailInput = document.getElementById('email');
        if (emailInput) emailInput.required = false;
        if (authBtn) authBtn.innerText = 'AUTHENTICATE';
        if (authToggleText) authToggleText.innerHTML = "Don't have an operative key? <span>Register here</span>";
        if (subtitle) subtitle.innerText = 'Neural Uplink Interface';
    } else {
        if (emailGroup) emailGroup.style.display = 'flex';
        const emailInput = document.getElementById('email');
        if (emailInput) emailInput.required = true;
        if (authBtn) authBtn.innerText = 'CREATE OPERATIVE';
        if (authToggleText) authToggleText.innerHTML = "Already registered? <span>Login here</span>";
        if (subtitle) subtitle.innerText = 'Register Operative Identity';
    }
}

async function handleAuth(event) {
    if (event && typeof event.preventDefault === 'function') event.preventDefault();
    const errorEl = document.getElementById('authError');
    errorEl.classList.add('hidden');

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email')?.value;

    try {
        let res;
        try {
            if (isLoginMode) {
                // Login relies on form data (OAuth2 standard used in FastAPI)
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('password', password);

                res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });
            } else {
                // Registration relies on JSON
                res = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
            }
        } catch (fetchErr) {
            throw new Error("Cannot connect to server. Ensure FastAPI backend is running on port 8000.");
        }

        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("text/html")) {
            throw new Error("API response is HTML instead of JSON. Check if Python backend is running on port 8000.");
        }
        
        let data;
        try {
            data = await res.json();
        } catch (jsonErr) {
            const text = await res.text();
            console.error("JSON Parse Error. Response text:", text);
            throw new Error(`Failed to parse JSON. Server returned: ${text.substring(0, 100)}...`);
        }

        if (isLoginMode) {
            if (res.ok) {
                state.token = data.access_token;
                state.user = username;
                localStorage.setItem('shadow_token', data.access_token);
                localStorage.setItem('shadow_user', username);
                navigate('chat');
            } else {
                throw new Error(data.detail || 'Authentication failed');
            }
        } else {
            if (res.ok) {
                // Auto login after register
                isLoginMode = true;
                handleAuth(event);
            } else {
                throw new Error(data.detail || 'Registration failed');
            }
        }
    } catch (err) {
        errorEl.innerText = 'SYSTEM ERROR: ' + err.message;
        errorEl.classList.remove('hidden');
    }
}

async function loginWithGoogleOAuth() {
    const errorEl = document.getElementById('authError');
    if (errorEl) errorEl.classList.add('hidden');
    window.location.href = `${API_BASE}/auth/login/google`;
}

function checkOAuthRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const user = urlParams.get('user');
    const error = urlParams.get('error');

    if (error) {
        setTimeout(() => {
            const errorEl = document.getElementById('authError');
            if (errorEl) {
                errorEl.innerText = "SYSTEM PROTOCOL ERROR: " + error;
                errorEl.classList.remove('hidden');
            }
        }, 150);
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
        return;
    }

    if (token && user) {
        state.token = token;
        state.user = user;
        localStorage.setItem('shadow_token', token);
        localStorage.setItem('shadow_user', user);

        // Clean query parameters from URL bar
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);

        if (typeof navigate === 'function') {
            navigate('chat');
        }
    }
}

// Execute OAuth redirect check immediately on script evaluation
checkOAuthRedirect();

async function logout() {
    state.token = null;
    state.user = null;
    state.currentSessionId = null;
    localStorage.removeItem('shadow_token');
    localStorage.removeItem('shadow_user');
    
    try {
        await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
    } catch (e) {
        console.warn("Logout cookie cleanup warning:", e);
    }

    navigate('chat');
}

function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.getElementById('passwordToggleBtn');
    if (!passwordInput || !toggleBtn) return;
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.innerText = 'Hide';
    } else {
        passwordInput.type = 'password';
        toggleBtn.innerText = 'Show';
    }
}

async function initGoogleSignIn() {
    try {
        const res = await fetch(`${API_BASE}/auth/config`);
        if (!res.ok) return;
        const config = await res.json();
        
        if (config.google_client_id && window.google && window.google.accounts) {
            google.accounts.id.initialize({
                client_id: config.google_client_id,
                callback: handleGoogleCredentialResponse,
                auto_select: false
            });
            // Display floating Google One Tap dialog overlay if available
            google.accounts.id.prompt();
        }
    } catch (err) {
        console.warn("Google One-Tap initialization info:", err);
    }
}

async function handleGoogleCredentialResponse(response) {
    const errorEl = document.getElementById('authError');
    if (errorEl) errorEl.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/auth/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential })
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Google authentication failed");
        }

        const data = await res.json();
        state.token = data.access_token;
        const payloadBase64 = data.access_token.split('.')[1];
        const payload = JSON.parse(atob(payloadBase64));
        const username = payload.sub || "GoogleUser";

        state.user = username;
        localStorage.setItem('shadow_token', data.access_token);
        localStorage.setItem('shadow_user', username);
        navigate('chat');
    } catch (err) {
        if (errorEl) {
            errorEl.innerText = 'SYSTEM ERROR: ' + err.message;
            errorEl.classList.remove('hidden');
        }
    }
}
