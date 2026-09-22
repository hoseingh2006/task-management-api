if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('projects');

let currentPage = 1;
const pageSize = 12;

async function loadProjects() {
    const list = document.getElementById('projectsList');
    showLoader(list);
    const params = { page: currentPage, page_size: pageSize };
    const status = document.getElementById('filterStatus').value;
    if (status) params.status = status;

    try {
        const res = await api.getProjects(params);
        const search = document.getElementById('searchInput').value.trim().toLowerCase();
        let items = res.items || [];
        if (search) items = items.filter(p => p.name.toLowerCase().includes(search));

        if (items.length === 0) {
            list.innerHTML = `<div class="empty"><div class="empty-icon">📁</div>No projects found</div>`;
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        list.innerHTML = `<div class="grid">${items.map(projectCard).join('')}</div>`;
        list.querySelectorAll('.project-card').forEach(el => {
            el.addEventListener('click', () => {
                window.location.href = `project.html?id=${el.dataset.id}`;
            });
        });

        renderPagination(document.getElementById('pagination'), res.page, res.pages, (p) => {
            currentPage = p;
            loadProjects();
        });
    } catch (err) {
        list.innerHTML = `<div class="empty">Failed to load: ${escapeHtml(err.message)}</div>`;
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

document.getElementById('filterStatus').addEventListener('change', () => { currentPage = 1; loadProjects(); });
document.getElementById('searchInput').addEventListener('input', () => loadProjects());
document.getElementById('newProjectBtn').addEventListener('click', () => modalOpen('projectModal'));

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
        currentPage = 1;
        loadProjects();
    } catch (err) { toast(err.message, 'error'); }
});

loadProjects();