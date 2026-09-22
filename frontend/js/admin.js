if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('admin');

// ===== Tabs =====
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        ['users', 'projects', 'tasks', 'tags', 'logs'].forEach(t => {
            document.getElementById('tab-' + t).style.display = 'none';
        });
        document.getElementById('tab-' + tab.dataset.tab).style.display = 'block';
        if (tab.dataset.tab === 'users') loadUsers();
        if (tab.dataset.tab === 'projects') loadProjects();
        if (tab.dataset.tab === 'tasks') loadTasks();
        if (tab.dataset.tab === 'tags') loadTags();
        if (tab.dataset.tab === 'logs') loadLogs();
    });
});

// ===== Dashboard stats =====
async function loadStats() {
    try {
        const d = await api.adminDashboard();
        document.getElementById('adminStats').innerHTML = `
      ${statCard('Active Users', d.user_active)}
      ${statCard('Inactive Users', d.user_deactivate)}
      ${statCard('Admins', d.admins)}
      ${statCard('Active Projects', d.project_active)}
      ${statCard('Inactive Projects', d.project_deactivate)}
      ${statCard('Active Tasks', d.task_active)}
      ${statCard('Inactive Tasks', d.task_deactivate)}
      ${statCard('User Logs', d.user_logs)}
      ${statCard('Admin Logs', d.admin_logs)}
    `;
    } catch (err) {
        toast('Admin access required: ' + err.message, 'error');
        setTimeout(() => window.location.href = 'dashboard.html', 1500);
    }
}

function statCard(label, value) {
    return `<div class="stat-card"><div class="stat-label">${escapeHtml(label)}</div><div class="stat-value">${value ?? 0}</div></div>`;
}

// ===== Users =====
let usersPage = 1;
async function loadUsers(page = 1) {
    usersPage = page;
    const list = document.getElementById('usersList');
    showLoader(list);
    const params = { page, page_size: 10 };
    const role = document.getElementById('userRoleFilter').value;
    const active = document.getElementById('userActiveFilter').value;
    if (role) params.role = role;
    if (active !== '') params.is_active = active === 'true';
    try {
        const res = await api.adminGetUsers(params);
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Username</th><th>Name</th><th>Email</th><th>Role</th><th>Active</th><th>Actions</th></tr></thead>
          <tbody>
            ${res.items.map(u => `
              <tr>
                <td>${u.id}</td>
                <td>${escapeHtml(u.username)}</td>
                <td>${escapeHtml(u.first_name + ' ' + u.last_name)}</td>
                <td>${escapeHtml(u.email)}</td>
                <td>${badge(u.role, u.role)}</td>
                <td>${u.is_active ? '✅' : '❌'}</td>
                <td>
                  <button class="btn btn-secondary btn-xs" data-action="edit" data-id="${u.id}">Edit</button>
                  <button class="btn btn-secondary btn-xs" data-action="pass" data-id="${u.id}">Password</button>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${u.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="edit"]').forEach(b => {
            b.addEventListener('click', () => editUser(res.items.find(x => x.id == b.dataset.id)));
        });
        list.querySelectorAll('[data-action="pass"]').forEach(b => {
            b.addEventListener('click', () => {
                const pwd = prompt('New password (min 6):');
                if (pwd && pwd.length >= 6) {
                    api.adminUpdateUserPassword(b.dataset.id, pwd)
                        .then(() => { toast('Password updated', 'success'); })
                        .catch(err => toast(err.message, 'error'));
                }
            });
        });
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete user?')) return;
                try {
                    await api.adminDeleteUser(b.dataset.id);
                    toast('Deleted', 'success');
                    loadUsers(usersPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('usersPagination'), res.page, res.pages, loadUsers);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

async function editUser(u) {
    const role = prompt('Role (user/admin):', u.role);
    if (role === null) return;
    const is_active = confirm('Is active? OK=yes, Cancel=no');
    try {
        await api.adminUpdateUser(u.id, { role, is_active });
        toast('User updated', 'success');
        loadUsers(usersPage);
    } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('userRoleFilter').addEventListener('change', () => loadUsers(1));
document.getElementById('userActiveFilter').addEventListener('change', () => loadUsers(1));

// ===== Projects =====
let projectsPage = 1;
async function loadProjects(page = 1) {
    projectsPage = page;
    const list = document.getElementById('projectsList2');
    showLoader(list);
    const params = { page, page_size: 10 };
    const status = document.getElementById('projStatusFilter').value;
    if (status) params.status = status;
    try {
        const res = await api.adminGetProjects(params);
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Active</th><th>Actions</th></tr></thead>
          <tbody>
            ${res.items.map(p => `
              <tr>
                <td>${p.id}</td>
                <td>${escapeHtml(p.name)}</td>
                <td>${statusBadge(p.status)}</td>
                <td>${p.is_active ? '✅' : '❌'}</td>
                <td>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${p.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete project?')) return;
                try {
                    await api.adminDeleteProject(b.dataset.id);
                    toast('Deleted', 'success');
                    loadProjects(projectsPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('projectsPagination'), res.page, res.pages, loadProjects);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}
document.getElementById('projStatusFilter').addEventListener('change', () => loadProjects(1));

// ===== Tasks =====
let tasksPage = 1;
async function loadTasks(page = 1) {
    tasksPage = page;
    const list = document.getElementById('tasksList2');
    showLoader(list);
    const params = { page, page_size: 10 };
    const status = document.getElementById('taskStatusFilter2').value;
    const priority = document.getElementById('taskPriorityFilter2').value;
    if (status) params.status = status;
    if (priority) params.priority = priority;
    try {
        const res = await api.adminGetTasks(params);
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Project</th><th>Title</th><th>Status</th><th>Priority</th><th>Active</th><th>Actions</th></tr></thead>
          <tbody>
            ${res.items.map(t => `
              <tr>
                <td>${t.id}</td>
                <td>${t.project_id}</td>
                <td>${escapeHtml(t.title)}</td>
                <td>${statusBadge(t.status)}</td>
                <td>${priorityBadge(t.priority)}</td>
                <td>${t.is_active ? '✅' : '❌'}</td>
                <td>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${t.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete task?')) return;
                try {
                    await api.adminDeleteTask(b.dataset.id);
                    toast('Deleted', 'success');
                    loadTasks(tasksPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('tasksPagination2'), res.page, res.pages, loadTasks);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}
document.getElementById('taskStatusFilter2').addEventListener('change', () => loadTasks(1));
document.getElementById('taskPriorityFilter2').addEventListener('change', () => loadTasks(1));

// ===== Tags =====
let tagsPage = 1;
async function loadTags(page = 1) {
    tagsPage = page;
    const list = document.getElementById('tagsList2');
    showLoader(list);
    try {
        const res = await api.adminGetTags({ page, page_size: 20 });
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Scope</th><th>Project</th><th>Actions</th></tr></thead>
          <tbody>
            ${res.items.map(t => `
              <tr>
                <td>${t.id}</td>
                <td>${escapeHtml(t.name)}</td>
                <td>${badge(t.scope, t.scope)}</td>
                <td>${t.project_id ?? '-'}</td>
                <td>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${t.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete tag?')) return;
                try {
                    await api.adminDeleteTag(b.dataset.id);
                    toast('Deleted', 'success');
                    loadTags(tagsPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('tagsPagination2'), res.page, res.pages, loadTags);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}
document.getElementById('createGlobalTagBtn').addEventListener('click', async () => {
    const name = document.getElementById('newGlobalTag').value.trim();
    if (!name) return;
    try {
        await api.adminCreateTag(name);
        toast('Global tag created', 'success');
        document.getElementById('newGlobalTag').value = '';
        loadTags(1);
    } catch (err) { toast(err.message, 'error'); }
});

// ===== Logs =====
let logsPage = 1;
async function loadLogs(page = 1) {
    logsPage = page;
    const list = document.getElementById('logsList');
    showLoader(list);
    const params = { page, page_size: 20 };
    const role = document.getElementById('logRoleFilter').value;
    if (role) params.role = role;
    try {
        const res = await api.adminGetLogs(params);
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Action</th><th>Description</th><th>Role</th><th>User</th><th>Project</th><th>Task</th><th>When</th></tr></thead>
          <tbody>
            ${res.items.map(l => `
              <tr>
                <td>${l.id}</td>
                <td><span class="chip">${escapeHtml(l.action)}</span></td>
                <td style="white-space:normal;max-width:320px;">${escapeHtml(l.description)}</td>
                <td>${badge(l.role, l.role)}</td>
                <td>${l.user_id ?? '-'}</td>
                <td>${l.project_id ?? '-'}</td>
                <td>${l.task_id ?? '-'}</td>
                <td>${fmtDate(l.created_at)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        renderPagination(document.getElementById('logsPagination'), res.page, res.pages, loadLogs);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}
document.getElementById('logRoleFilter').addEventListener('change', () => loadLogs(1));

// ===== Init =====
loadStats();
loadUsers();