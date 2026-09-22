if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('notifications');

let currentProjectId = null;
let projects = [];
let currentPage = 1;

async function initProjects() {
    try {
        const res = await api.getProjects({ page: 1, page_size: 100 });
        projects = res.items || [];
        const sel = document.getElementById('notifProjectSelect');
        sel.innerHTML = `<option value="">All Projects</option>` +
            projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
        sel.addEventListener('change', () => {
            currentProjectId = sel.value || null;
            loadNotifications(1);
        });
        // default to first project
        if (projects.length > 0) {
            currentProjectId = projects[0].id;
            sel.value = String(currentProjectId);
        }
    } catch (e) { }
    loadNotifications(1);
}

async function loadNotifications(page = 1) {
    currentPage = page;
    const list = document.getElementById('notificationsList');
    showLoader(list);
    if (!currentProjectId) {
        // For "all projects", we still need a project_id due to backend route design.
        // Notifications endpoints are under /project/{project_id}/task/notification
        // so we must show per project.
        if (projects.length === 0) {
            list.innerHTML = `<div class="empty">No projects</div>`;
            return;
        }
        currentProjectId = projects[0].id;
        document.getElementById('notifProjectSelect').value = String(currentProjectId);
    }
    const type = document.getElementById('notifTypeFilter').value;
    const params = { page, page_size: 10 };
    if (type) params.notification_type = type;
    try {
        const res = await api.getNotifications(currentProjectId, params);
        if (!res.items || res.items.length === 0) {
            list.innerHTML = `<div class="empty"><div class="empty-icon">🔔</div>No notifications</div>`;
            document.getElementById('notifPagination').innerHTML = '';
            return;
        }
        list.innerHTML = res.items.map(n => `
      <div class="card" style="${n.is_read ? '' : 'border-left:4px solid var(--primary);'}">
        <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">
          <div style="flex:1;min-width:200px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
              <strong>${escapeHtml(n.title)}</strong>
              <span class="badge badge-${n.is_read ? 'archived' : 'active'}">${n.is_read ? 'read' : 'unread'}</span>
              <span class="chip">${escapeHtml(n.type)}</span>
            </div>
            <div style="font-size:14px;color:var(--gray-700);">${escapeHtml(n.message)}</div>
            <div style="font-size:12px;color:var(--gray-500);margin-top:6px;">${fmtDate(n.created_at)}</div>
          </div>
          <div style="display:flex;gap:6px;align-items:start;">
            ${!n.is_read ? `<button class="btn btn-secondary btn-xs" data-action="read" data-id="${n.id}">Mark read</button>` : ''}
            <button class="btn btn-danger btn-xs" data-action="del" data-id="${n.id}">Delete</button>
          </div>
        </div>
      </div>
    `).join('');
        list.querySelectorAll('[data-action="read"]').forEach(b => {
            b.addEventListener('click', async () => {
                try {
                    await api.markNotificationRead(currentProjectId, b.dataset.id);
                    toast('Marked as read', 'success');
                    loadNotifications(currentPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete notification?')) return;
                try {
                    await api.deleteNotification(currentProjectId, b.dataset.id);
                    toast('Deleted', 'success');
                    loadNotifications(currentPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('notifPagination'), res.page, res.pages, loadNotifications);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

document.getElementById('notifTypeFilter').addEventListener('change', () => loadNotifications(1));
document.getElementById('markAllReadBtn').addEventListener('click', async () => {
    if (!currentProjectId) return;
    try {
        await api.markAllRead(currentProjectId);
        toast('All marked as read', 'success');
        loadNotifications(currentPage);
    } catch (err) { toast(err.message, 'error'); }
});

initProjects();