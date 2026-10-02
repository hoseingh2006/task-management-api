// ============ API Layer ============
const API_BASE = '/api'; // change if needed

const Auth = {
  getToken() { return localStorage.getItem('token'); },
  setToken(t) { localStorage.setItem('token', t); },
  clear() { localStorage.removeItem('token'); },
  isLoggedIn() { return !!this.getToken(); },
  logout() { this.clear(); window.location.href = 'index.html'; },
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = 'index.html';
      return false;
    }
    return true;
  }
};

/**
 * Generic fetch wrapper
 */
async function apiRequest(path, { method = 'GET', body = null, form = false, isFormData = false } = {}) {
  const headers = {};
  const token = Auth.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let payload = null;
  if (body) {
    if (form) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
      payload = new URLSearchParams(body).toString();
    } else if (isFormData) {
      payload = body; // FormData
    } else {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: payload,
  });

  // Handle 401
  if (res.status === 401) {
    Auth.clear();
    if (!path.startsWith('/token') && !path.startsWith('/user/')) {
      // Only redirect if not on login page
      if (!window.location.pathname.endsWith('index.html') &&
        !window.location.pathname.endsWith('register.html') &&
        window.location.pathname !== '/') {
        window.location.href = 'index.html';
      }
    }
  }

  let data = null;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    data = await res.json().catch(() => null);
  } else {
    const text = await res.text();
    data = text ? { detail: text } : null;
  }

  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || `Error ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

const api = {
  // ===== AUTH =====
  login: (username, password) =>
    apiRequest('/token', { method: 'POST', body: { username, password }, form: true }),

  // ===== USER =====
  register: (data) => apiRequest('/user/', { method: 'POST', body: data }),
  getMe: () => apiRequest('/user/'),
  updateMe: (data) => apiRequest('/user/', { method: 'PUT', body: data }),
  updatePassword: (data) => apiRequest('/user/password', { method: 'PUT', body: data }),

  // ===== PROJECTS =====
  createProject: (data) => apiRequest('/project/', { method: 'POST', body: data }),
  getProjects: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/?${q}`);
  },
  getProject: (id) => apiRequest(`/project/${id}`),
  updateProject: (id, data) => apiRequest(`/project/${id}`, { method: 'PUT', body: data }),
  deleteProject: (id) => apiRequest(`/project/${id}`, { method: 'DELETE' }),
  updateProjectStatus: (id, status) =>
    apiRequest(`/project/${id}/status`, { method: 'PATCH', body: { status } }),

  // Members
  addMember: (projectId, data) =>
    apiRequest(`/project/${projectId}/member`, { method: 'POST', body: data }),
  updateMember: (projectId, userId, role) =>
    apiRequest(`/project/${projectId}/members/${userId}`, { method: 'PATCH', body: { role } }),
  getMembers: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 50, ...params });
    return apiRequest(`/project/${projectId}/members/?${q}`);
  },
  removeMember: (projectId, userId) =>
    apiRequest(`/project/${projectId}/members/${userId}`, { method: 'DELETE' }),

  // ===== TASKS =====
  createTask: (projectId, data) =>
    apiRequest(`/project/${projectId}/task/`, { method: 'POST', body: data }),
  getTasks: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/?${q}`);
  },
  getTask: (projectId, taskId) =>
    apiRequest(`/project/${projectId}/task/${taskId}`),
  updateTask: (projectId, taskId, data) =>
    apiRequest(`/project/${projectId}/task/${taskId}`, { method: 'PUT', body: data }),
  deleteTask: (projectId, taskId) =>
    apiRequest(`/project/${projectId}/task/${taskId}`, { method: 'DELETE' }),
  updateTaskStatus: (projectId, taskId, status) =>
    apiRequest(`/project/${projectId}/task/status/${taskId}`, { method: 'PATCH', body: { status } }),

  // Tags
  createProjectTag: (projectId, data) =>
    apiRequest(`/project/${projectId}/task/tag`, { method: 'POST', body: data }),
  updateProjectTag: (projectId, tagId, data) =>
    apiRequest(`/project/${projectId}/task/tag/${tagId}`, { method: 'PUT', body: data }),
  deleteProjectTag: (projectId, tagId) =>
    apiRequest(`/project/${projectId}/task/tag/${tagId}`, { method: 'DELETE' }),
  getProjectTags: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 50, ...params });
    return apiRequest(`/project/${projectId}/task/tag?${q}`);
  },
  getTaskTags: (projectId, taskId) =>
    apiRequest(`/project/${projectId}/task/tag/task/${taskId}`),
  addTagsToTask: (projectId, taskId, tagIds) =>
    apiRequest(`/project/${projectId}/task/tag/task/${taskId}`, {
      method: 'POST', body: { tags_id: tagIds }
    }),

  // Subtasks
  createSubtask: (projectId, taskId, data) =>
    apiRequest(`/project/${projectId}/task/subtask/${taskId}`, { method: 'POST', body: data }),
  getSubtasks: (projectId, taskId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/subtask/${taskId}?${q}`);
  },
  updateSubtask: (projectId, taskId, subId, data) =>
    apiRequest(`/project/${projectId}/task/subtask/${taskId}/${subId}`, { method: 'PUT', body: data }),
  deleteSubtask: (projectId, taskId, subId) =>
    apiRequest(`/project/${projectId}/task/subtask/${taskId}/${subId}`, { method: 'DELETE' }),

  // Dependencies
  getDependencies: (projectId, taskId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/depends/${taskId}?${q}`);
  },
  deleteDependency: (projectId, taskId, depIds) =>
    apiRequest(`/project/${projectId}/task/depends/${taskId}`, {
      method: 'DELETE', body: { dependency_ids: depIds }
    }),

  // Comments
  addComment: (projectId, taskId, content) =>
    apiRequest(`/project/${projectId}/task/${taskId}/comments`, {
      method: 'POST', body: { content }
    }),
  getComments: (projectId, taskId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/${taskId}/comments?${q}`);
  },
  updateComment: (projectId, taskId, commentId, content) =>
    apiRequest(`/project/${projectId}/task/${taskId}/comments/${commentId}`, {
      method: 'PUT', body: { content }
    }),
  deleteComment: (projectId, taskId, commentId) =>
    apiRequest(`/project/${projectId}/task/${taskId}/comments/${commentId}`, { method: 'DELETE' }),

  // Notifications
  getNotifications: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/notification?${q}`);
  },
  getUnreadNotifications: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/project/${projectId}/task/notification/unread?${q}`);
  },
  markNotificationRead: (projectId, id) =>
    apiRequest(`/project/${projectId}/task/notification/${id}/read`, { method: 'PATCH' }),
  markAllRead: (projectId) =>
    apiRequest(`/project/${projectId}/task/notification/read-all`, { method: 'PATCH' }),
  deleteNotification: (projectId, id) =>
    apiRequest(`/project/${projectId}/task/notification/${id}`, { method: 'DELETE' }),

  // ===== ADMIN =====
  adminGetUsers: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/users?${q}`);
  },
  adminGetUser: (id) => apiRequest(`/admin/users/${id}`),
  adminUpdateUser: (id, data) => apiRequest(`/admin/users/${id}`, { method: 'PUT', body: data }),
  adminUpdateUserPassword: (id, password) =>
    apiRequest(`/admin/users/password/${id}`, { method: 'PUT', body: { password } }),
  adminDeleteUser: (id) => apiRequest(`/admin/users/${id}`, { method: 'DELETE' }),

  adminGetProjects: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/projects?${q}`);
  },
  adminGetProject: (id) => apiRequest(`/admin/projects/${id}`),
  adminDeleteProject: (id) => apiRequest(`/admin/projects/${id}`, { method: 'DELETE' }),
  adminGetProjectMembers: (id, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 50, ...params });
    return apiRequest(`/admin/projects/${id}/members?${q}`);
  },

  adminGetTasks: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/tasks?${q}`);
  },
  adminGetTask: (id) => apiRequest(`/admin/tasks/${id}`),
  adminDeleteTask: (id) => apiRequest(`/admin/tasks/${id}`, { method: 'DELETE' }),

  adminDashboard: () => apiRequest('/admin/dashboard'),

  adminGetTags: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/tag?${q}`);
  },
  adminCreateTag: (name) => apiRequest('/admin/tag', { method: 'POST', body: { name } }),
  adminUpdateTag: (id, name) => apiRequest(`/admin/tag/${id}`, { method: 'PUT', body: { name } }),
  adminDeleteTag: (id) => apiRequest(`/admin/tag/${id}`, { method: 'DELETE' }),

  adminGetSubtasks: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/subtask?${q}`);
  },
  adminGetSubtask: (id) => apiRequest(`/admin/subtask/${id}`),

  adminGetLogs: (params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/logs?${q}`);
  },
  adminGetLogsByUser: (userId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/logs/user/${userId}?${q}`);
  },
  adminGetLogsByTask: (taskId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/logs/task/task/${taskId}?${q}`);
  },
  adminGetLogsByProject: (projectId, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/logs/project/${projectId}?${q}`);
  },
  adminGetLogsByAction: (action, params = {}) => {
    const q = new URLSearchParams({ page: 1, page_size: 20, ...params });
    return apiRequest(`/admin/logs/action/action/${action}?${q}`);
  },
};

// ============ UI helpers ============

function toast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function showLoader(container) {
  container.innerHTML = '<div class="loader"></div>';
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function fmtDate(d) {
  if (!d) return '-';
  try {
    const dt = new Date(d);
    return dt.toLocaleDateString() + ' ' + dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch { return d; }
}

function fmtDateShort(d) {
  if (!d) return '-';
  try { return new Date(d).toLocaleDateString(); } catch { return d; }
}

function badge(text, cls) {
  return `<span class="badge badge-${cls}">${escapeHtml(text)}</span>`;
}

function statusBadge(s) {
  return badge(s, s);
}

function priorityBadge(p) {
  return badge(p, p);
}

function roleBadge(r) {
  return badge(r, r);
}

/**
 * Generic pagination renderer
 */
function renderPagination(el, page, pages, onPage) {
  if (pages <= 1) { el.innerHTML = ''; return; }
  let html = '';
  html += `<button ${page <= 1 ? 'disabled' : ''} data-p="${page - 1}">‹</button>`;
  const start = Math.max(1, page - 2);
  const end = Math.min(pages, page + 2);
  if (start > 1) html += `<button data-p="1">1</button>`;
  if (start > 2) html += `<span>…</span>`;
  for (let i = start; i <= end; i++) {
    html += `<button class="${i === page ? 'active' : ''}" data-p="${i}">${i}</button>`;
  }
  if (end < pages - 1) html += `<span>…</span>`;
  if (end < pages) html += `<button data-p="${pages}">${pages}</button>`;
  html += `<button ${page >= pages ? 'disabled' : ''} data-p="${page + 1}">›</button>`;
  el.innerHTML = html;
  el.querySelectorAll('button[data-p]').forEach(b => {
    b.addEventListener('click', () => onPage(parseInt(b.dataset.p)));
  });
}

function confirmDialog(message) {
  return window.confirm(message);
}

// Sidebar helper for all authenticated pages
function initSidebar(activeName) {
  const toggle = document.querySelector('.menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (backdrop) backdrop.classList.toggle('open');
    });
    if (backdrop) {
      backdrop.addEventListener('click', () => {
        sidebar.classList.remove('open');
        backdrop.classList.remove('open');
      });
    }
  }
  // mark active
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    if (a.dataset.name === activeName) a.classList.add('active');
  });

  // logout
  const logoutBtn = document.querySelector('#logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => Auth.logout());
  }

  // load user info in topbar
  const nameEl = document.querySelector('#userName');
  const avatarEl = document.querySelector('#userAvatar');
  const adminLink = document.querySelector('#adminLink');
  if (nameEl) {
    api.getMe().then(u => {
      nameEl.textContent = u.FirstName + ' ' + u.LastName;
      if (avatarEl) {
        avatarEl.textContent = (u.FirstName?.[0] || '') + (u.LastName?.[0] || '');
      }
      if (adminLink) {
        // we don't know role from /user/ endpoint; try admin dashboard
        api.adminDashboard()
          .then(() => { adminLink.style.display = 'flex'; })
          .catch(() => { adminLink.style.display = 'none'; });
      }
    }).catch(() => { });
  }
}

function modalOpen(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}
function modalClose(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}
// ============================================================
// Helper: read selected IDs from <select multiple>
// ============================================================
function getSelectedIds(selectId) {
  const el = document.getElementById(selectId);
  if (!el) return [];
  return Array.from(el.selectedOptions)
    .map(o => parseInt(o.value, 10))
    .filter(n => !isNaN(n));
}

// ============================================================
// Helper: parse comma-separated IDs string into array
// ============================================================
function parseIdsString(str) {
  if (!str || !str.trim()) return [];
  return str
    .split(',')
    .map(s => parseInt(s.trim(), 10))
    .filter(n => !isNaN(n));
}

// ============================================================
// Helper: close modal by clicking backdrop
// ============================================================
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('open')) {
    e.target.classList.remove('open');
  }
});