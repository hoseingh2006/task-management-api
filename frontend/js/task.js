if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('projects');

const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const taskId = urlParams.get('id');
if (!projectId || !taskId) { window.location.href = 'projects.html'; }

let task = null;
let availableProjectTags = [];

// ===== Tabs =====
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        ['subtasks', 'comments', 'dependencies', 'tags'].forEach(t => {
            document.getElementById('tab-' + t).style.display = 'none';
        });
        document.getElementById('tab-' + tab.dataset.tab).style.display = 'block';
        if (tab.dataset.tab === 'dependencies') loadDeps();
        if (tab.dataset.tab === 'tags') loadTaskTags();
    });
});

// ===== Load task =====
async function loadTask() {
    try {
        task = await api.getTask(projectId, taskId);
        document.getElementById('taskTitle').textContent = task.title;
        document.getElementById('taskInfo').innerHTML = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:start;gap:12px;flex-wrap:wrap;">
          <div style="flex:1;min-width:250px;">
            <div style="font-size:13px;color:var(--gray-500);margin-bottom:4px;">Description</div>
            <div>${escapeHtml(task.description || 'No description')}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">
              ${statusBadge(task.status)}
              ${priorityBadge(task.priority)}
              <span class="chip">Due: ${fmtDate(task.due_date)}</span>
              <span class="chip">Creator #${task.creator_id}</span>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:8px;align-items:flex-end;">
            <button class="btn btn-secondary btn-sm" id="editTaskBtn">✏️ Edit</button>
            <button class="btn btn-danger btn-sm" id="deleteTaskBtn">🗑️ Delete</button>
            <button class="btn btn-secondary btn-sm" id="backBtn">← Back</button>
          </div>
        </div>
      </div>
    `;
        document.getElementById('editTaskBtn').addEventListener('click', () => {
            window.location.href = `project.html?id=${projectId}`;
            setTimeout(() => {
                // Fallback: just go to project page
            }, 100);
        });
        document.getElementById('deleteTaskBtn').addEventListener('click', deleteTask);
        document.getElementById('backBtn').addEventListener('click', () => {
            window.location.href = `project.html?id=${projectId}`;
        });
        loadSubtasks();
        loadComments();
        loadDeps();
        loadTaskTags();
        loadAvailableTags();
    } catch (err) {
        toast(err.message, 'error');
        setTimeout(() => window.location.href = `project.html?id=${projectId}`, 1500);
    }
}

async function deleteTask() {
    if (!confirmDialog('Delete this task?')) return;
    try {
        await api.deleteTask(projectId, taskId);
        toast('Task deleted', 'success');
        setTimeout(() => window.location.href = `project.html?id=${projectId}`, 700);
    } catch (err) { toast(err.message, 'error'); }
}

// ===== Subtasks =====
let subtasksPage = 1;
async function loadSubtasks(page = 1) {
    subtasksPage = page;
    const list = document.getElementById('subtasksList');
    showLoader(list);
    try {
        const res = await api.getSubtasks(projectId, taskId, { page, page_size: 10 });
        if (!res.items || res.items.length === 0) {
            list.innerHTML = `<div class="empty">No subtasks yet</div>`;
            document.getElementById('subtasksPagination').innerHTML = '';
            return;
        }
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th><th>Due</th><th>Actions</th></tr></thead>
          <tbody>
            ${res.items.map(s => `
              <tr>
                <td>${s.id}</td>
                <td>${escapeHtml(s.title)}</td>
                <td>${statusBadge(s.status)}</td>
                <td>${priorityBadge(s.priority)}</td>
                <td>${fmtDateShort(s.due_date)}</td>
                <td>
                  <button class="btn btn-secondary btn-xs" data-action="edit" data-id="${s.id}">Edit</button>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${s.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="edit"]').forEach(b => {
            b.addEventListener('click', () => openSubtaskModal(res.items.find(x => x.id == b.dataset.id)));
        });
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', () => deleteSubtask(b.dataset.id));
        });
        renderPagination(document.getElementById('subtasksPagination'), res.page, res.pages, loadSubtasks);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

document.getElementById('newSubtaskBtn').addEventListener('click', () => openSubtaskModal(null));

function openSubtaskModal(s) {
    document.getElementById('subtaskModalTitle').textContent = s ? 'Edit Subtask' : 'New Subtask';
    document.getElementById('subtaskId').value = s?.id || '';
    document.getElementById('subtaskTitle').value = s?.title || '';
    document.getElementById('subtaskDesc').value = s?.description || '';
    document.getElementById('subtaskPriority').value = s?.priority || '';
    document.getElementById('subtaskDueValue').value = '';
    document.getElementById('subtaskDueUnit').value = '';
    modalOpen('subtaskModal');
}

document.getElementById('subtaskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const sid = document.getElementById('subtaskId').value;
    const payload = {
        title: document.getElementById('subtaskTitle').value.trim(),
        description: document.getElementById('subtaskDesc').value.trim() || null,
    };
    const pr = document.getElementById('subtaskPriority').value;
    if (pr) payload.priority = pr;
    const dv = document.getElementById('subtaskDueValue').value;
    const du = document.getElementById('subtaskDueUnit').value;
    if (dv && du) { payload.due_value = parseInt(dv); payload.due_unit = du; }

    try {
        if (sid) {
            await api.updateSubtask(projectId, taskId, sid, payload);
            toast('Subtask updated', 'success');
        } else {
            payload.assignee_ids = [];
            payload.tags_id = [];
            payload.dependency_ids = [];
            await api.createSubtask(projectId, taskId, payload);
            toast('Subtask created', 'success');
        }
        modalClose('subtaskModal');
        loadSubtasks(subtasksPage);
    } catch (err) { toast(err.message, 'error'); }
});

async function deleteSubtask(id) {
    if (!confirmDialog('Delete subtask?')) return;
    try {
        await api.deleteSubtask(projectId, taskId, id);
        toast('Subtask deleted', 'success');
        loadSubtasks(subtasksPage);
    } catch (err) { toast(err.message, 'error'); }
}

// ===== Comments =====
let commentsPage = 1;
async function loadComments(page = 1) {
    commentsPage = page;
    const list = document.getElementById('commentsList');
    showLoader(list);
    try {
        const res = await api.getComments(projectId, taskId, { page, page_size: 10 });
        if (!res.items || res.items.length === 0) {
            list.innerHTML = `<div class="empty">No comments yet</div>`;
            document.getElementById('commentsPagination').innerHTML = '';
            return;
        }
        list.innerHTML = res.items.map(c => `
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">
          <div style="font-size:12px;color:var(--gray-500);">User #${c.creator_id} · ${fmtDate(c.created_at)}</div>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-secondary btn-xs" data-action="edit" data-id="${c.id}">Edit</button>
            <button class="btn btn-danger btn-xs" data-action="del" data-id="${c.id}">Delete</button>
          </div>
        </div>
        <div style="margin-top:8px;white-space:pre-wrap;">${escapeHtml(c.content)}</div>
      </div>
    `).join('');
        list.querySelectorAll('[data-action="edit"]').forEach(b => {
            b.addEventListener('click', () => {
                const c = res.items.find(x => x.id == b.dataset.id);
                const newContent = prompt('Edit comment:', c.content);
                if (newContent !== null && newContent.trim()) {
                    api.updateComment(projectId, taskId, c.id, newContent.trim())
                        .then(() => { toast('Comment updated', 'success'); loadComments(commentsPage); })
                        .catch(err => toast(err.message, 'error'));
                }
            });
        });
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', async () => {
                if (!confirmDialog('Delete comment?')) return;
                try {
                    await api.deleteComment(projectId, taskId, b.dataset.id);
                    toast('Comment deleted', 'success');
                    loadComments(commentsPage);
                } catch (err) { toast(err.message, 'error'); }
            });
        });
        renderPagination(document.getElementById('commentsPagination'), res.page, res.pages, loadComments);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

document.getElementById('postCommentBtn').addEventListener('click', async () => {
    const content = document.getElementById('newComment').value.trim();
    if (!content) return;
    try {
        await api.addComment(projectId, taskId, content);
        document.getElementById('newComment').value = '';
        toast('Comment posted', 'success');
        loadComments(1);
    } catch (err) { toast(err.message, 'error'); }
});

// ===== Dependencies =====
async function loadDeps(page = 1) {
    const list = document.getElementById('depsList');
    showLoader(list);
    try {
        const res = await api.getDependencies(projectId, taskId, { page, page_size: 20 });
        if (!res.items || res.items.length === 0) {
            list.innerHTML = `<div class="empty">No dependencies</div>`;
            document.getElementById('depsPagination').innerHTML = '';
            return;
        }
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th></tr></thead>
          <tbody>
            ${res.items.map(d => `
              <tr>
                <td>${d.id}</td>
                <td>${escapeHtml(d.title)}</td>
                <td>${statusBadge(d.status)}</td>
                <td>${priorityBadge(d.priority)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        renderPagination(document.getElementById('depsPagination'), res.page, res.pages, loadDeps);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

// ===== Tags =====
async function loadTaskTags() {
    const list = document.getElementById('taskTagsList');
    showLoader(list);
    try {
        const tags = await api.getTaskTags(projectId, taskId);
        if (!tags || tags.length === 0) {
            list.innerHTML = `<div class="empty">No tags on this task</div>`;
            return;
        }
        list.innerHTML = `<div class="chips">${tags.map(t => `<span class="chip">${escapeHtml(t.name)} <span class="badge badge-${t.scope}">${t.scope}</span></span>`).join('')}</div>`;
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

async function loadAvailableTags() {
    try {
        const res = await api.getProjectTags(projectId, { page: 1, page_size: 100 });
        availableProjectTags = res.items || [];
    } catch (e) { }
}

document.getElementById('manageTagsBtn').addEventListener('click', () => {
    const sel = document.getElementById('availableTags');
    sel.innerHTML = availableProjectTags.map(t =>
        `<option value="${t.id}">${escapeHtml(t.name)} [${t.scope}]</option>`
    ).join('');
    modalOpen('tagsModal');
});

document.getElementById('addTagsSubmit').addEventListener('click', async () => {
    const ids = Array.from(document.getElementById('availableTags').selectedOptions).map(o => parseInt(o.value));
    if (!ids.length) return toast('Select at least one tag', 'warning');
    try {
        await api.addTagsToTask(projectId, taskId, ids);
        toast('Tags added', 'success');
        modalClose('tagsModal');
        loadTaskTags();
    } catch (err) { toast(err.message, 'error'); }
});

loadTask();