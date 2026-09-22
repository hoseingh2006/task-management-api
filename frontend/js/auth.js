// Redirect if already logged in
if (Auth.isLoggedIn()) {
    // try to see if we can hit /user/ (any logged in user)
    api.getMe().then(() => {
        window.location.href = 'dashboard.html';
    }).catch(() => { });
}

// ===== Login =====
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('loginBtn');
        btn.disabled = true;
        btn.textContent = 'Signing in...';
        try {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const data = await api.login(username, password);
            Auth.setToken(data.access_token);
            toast('Login successful!', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 500);
        } catch (err) {
            toast(err.message, 'error');
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    });
}

// ===== Register =====
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('regBtn');
        btn.disabled = true;
        btn.textContent = 'Creating...';
        try {
            await api.register({
                first_name: document.getElementById('firstName').value.trim(),
                last_name: document.getElementById('lastName').value.trim(),
                username: document.getElementById('username').value.trim(),
                email: document.getElementById('email').value.trim(),
                password: document.getElementById('password').value,
            });
            toast('Account created! You can now log in.', 'success');
            setTimeout(() => window.location.href = 'index.html', 900);
        } catch (err) {
            toast(err.message, 'error');
            btn.disabled = false;
            btn.textContent = 'Create Account';
        }
    });
}