if (!Auth.requireAuth()) throw new Error('auth');

initSidebar('dashboard');

let userProjects = [];

async function loadDashboard() {
    try {
        const res = await api.getProjects({ page: 1, page_size: 100 });
        userProjects = res.items || [];

        document.getElementById('statProjects').textContent = res.total ?? 0;
        document.getElementById('statActive').textContent =
            userProjects.filter(p => p.status === 'active').length;
        document.getElementById('statCompleted').textContent =
            userProjects.filter(p => p.status === 'completed').length;
        document.getElementById('statArchived').textContent =
            userProjects.filter(p => p.status === 'archived').length;

        const recent = document.getElementById('recentProjects');
        if (userProjects.length === 0) {
            recent.innerHTML = `<div class="empty"><div class="empty-icon">📁</div>No projects yet. Create your first one!</div>`;
            return;
        }
        recent.innerHTML = `<div class="grid">${userProjects.slice(0, 6).map(projectCard).join('')}</div>`;
        recent.querySelectorAll('.project-card').forEach(el => {
            el.addEventListener('click', () => {
                window.location.href = `project.html?id=${el.dataset.id}`;
            });
        });
    } catch (err) {
        toast(err.message, 'error');
    }
}

function projectCard(p) {
    return `
    <div class="project-card" data-id="${p.id}">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">
        <h3>${escapeHtml(p.name)}</h3>
        ${statusBadge(p.status)}
      </div>
      <p class="desc">${escapeHtml(p.description || 'No description')}</p>
      <div style="font-size:12px;color:var(--gray-500);">Created ${fmtDateShort(p.created_at)}</div>
    </div>
  `;
}

loadDashboard();

// New project
document.getElementById('newProjectBtn').addEventListener('click', () => {
    modalOpen('projectModal');
});

document.getElementById('newProjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await api.createProject({
            name: document.getElementById('projName').value.trim(),
            description: document.getElementById('projDesc').value.trim() || null,
        });
        toast('Project created!', 'success');
        modalClose('projectModal');
        document.getElementById('newProjectForm').reset();
        loadDashboard();
    } catch (err) {
        toast(err.message, 'error');
    }
});