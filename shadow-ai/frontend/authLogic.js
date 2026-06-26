// Continuation of app logic for Shadow AI

let isLoginMode = true;

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const emailGroup = document.getElementById('emailGroup');
    const authBtn = document.getElementById('authBtn');
    const authToggleText = document.getElementById('authToggleText');
    const title = document.querySelector('#authForm').previousElementSibling;

    if (isLoginMode) {
        emailGroup.style.display = 'none';
        document.getElementById('email').required = false;
        authBtn.innerText = 'INITIALIZE SYSTEM';
        authToggleText.innerText = 'NEW_OPERATIVE? REGISTER_HERE';
        title.innerText = 'AUTH PROTOCOL';
    } else {
        emailGroup.style.display = 'flex';
        document.getElementById('email').required = true;
        authBtn.innerText = 'INITIALIZE NEW IDENTITY';
        authToggleText.innerText = 'EXISTING_OPERATIVE? LOGIN_HERE';
        title.innerText = 'CREATE OPERATIVE';
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

function logout() {
    state.token = null;
    state.user = null;
    state.currentSessionId = null;
    localStorage.removeItem('shadow_token');
    localStorage.removeItem('shadow_user');
    navigate('chat');
}
