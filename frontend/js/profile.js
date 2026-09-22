if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('profile');

async function loadProfile() {
    try {
        const u = await api.getMe();
        document.getElementById('pUsername').value = u.UserName || '';
        document.getElementById('pFirstName').value = u.FirstName || '';
        document.getElementById('pLastName').value = u.LastName || '';
        document.getElementById('pEmail').value = u.Email || '';
    } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await api.updateMe({
            username: document.getElementById('pUsername').value.trim() || null,
            first_name: document.getElementById('pFirstName').value.trim() || null,
            last_name: document.getElementById('pLastName').value.trim() || null,
            email: document.getElementById('pEmail').value.trim() || null,
        });
        toast('Profile updated', 'success');
        loadProfile();
    } catch (err) { toast(err.message, 'error'); }
});

document.getElementById('passForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await api.updatePassword({
            old_password: document.getElementById('oldPass').value,
            new_password: document.getElementById('newPass').value,
        });
        toast('Password changed', 'success');
        document.getElementById('passForm').reset();
    } catch (err) { toast(err.message, 'error'); }
});

loadProfile();