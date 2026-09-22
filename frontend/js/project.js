if (!Auth.requireAuth()) throw new Error('auth');
initSidebar('projects');

const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('id');
if (!projectId) { window.location.href = 'projects.html'; }

let project = null;
let members = [];
let allTags = [];
let myRole = null;
let currentTasksPage = 1;
let currentMembersPage = 1;
let currentTagsPage = 1;

// ============================================================
// Tabs
// ============================================================
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        ['tasks', 'members', 'tags'].forEach(t => {
            document.getElementById('tab-' + t).style.display = 'none';
        });
        document.getElementById('tab-' + tab.dataset.tab).style.display = 'block';
    });
});

// ============================================================
// Load project
// ============================================================
async function loadProject() {
    try {
        project = await api.getProject(projectId);
        document.getElementById('projectTitle').textContent = project.name;

        await detectMyRole();

        const canManage = myRole === 'owner' || myRole === 'manager';
        const isOwner = myRole === 'owner';

        document.getElementById('projectInfo').innerHTML = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:start;gap:12px;flex-wrap:wrap;">
          <div style="flex:1;min-width:220px;">
            <div style="font-size:13px;color:var(--gray-500);margin-bottom:4px;">Description</div>
            <div>${escapeHtml(project.description || 'No description')}</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:8px;align-items:flex-end;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              ${statusBadge(project.status)}
              <span class="chip">Your role: ${escapeHtml(myRole || 'unknown')}</span>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;">
              ${canManage ? `<button class="btn btn-secondary btn-sm" id="changeStatusBtn">🔄 Change Status</button>` : ''}
              ${canManage ? `<button class="btn btn-secondary btn-sm" id="editProjectBtn">✏️ Edit</button>` : ''}
              ${isOwner ? `<button class="btn btn-danger btn-sm" id="deleteProjectBtn">🗑️ Delete</button>` : ''}
            </div>
          </div>
        </div>
        <div style="font-size:12px;color:var(--gray-500);margin-top:12px;">
          Created ${fmtDate(project.created_at)} · Updated ${fmtDate(project.updated_at)}
        </div>
      </div>
    `;

        document.getElementById('changeStatusBtn')?.addEventListener('click', changeProjectStatus);
        document.getElementById('editProjectBtn')?.addEventListener('click', editProject);
        document.getElementById('deleteProjectBtn')?.addEventListener('click', deleteProject);

        loadMembers();
        loadTags();
        loadTasks();
    } catch (err) {
        toast(err.message, 'error');
        setTimeout(() => window.location.href = 'projects.html', 1500);
    }
}

async function detectMyRole() {
    try {
        const me = await api.getMe();
        const res = await api.getMembers(projectId, { page: 1, page_size: 100 });
        const mine = (res.items || []).find(m => m.username === me.UserName);
        myRole = mine ? mine.role : null;
    } catch (e) {
        myRole = null;
    }
}

// ============================================================
// Change project status
// ============================================================
function changeProjectStatus() {
    document.getElementById('currentStatusBadge').innerHTML =
        statusBadge(project.status);

    const radios = document.querySelectorAll('input[name="projStatus"]');
    const labels = document.querySelectorAll('.status-option');

    labels.forEach(l => l.classList.remove('selected', 'disabled'));
    radios.forEach(r => {
        r.checked = false;
        if (r.value === project.status) {
            r.closest('.status-option').classList.add('disabled');
        }
    });

    document.querySelectorAll('.status-option').forEach(label => {
        label.onclick = () => {
            if (label.classList.contains('disabled')) return;
            document.querySelectorAll('.status-option').forEach(l => l.classList.remove('selected'));
            label.classList.add('selected');
            const radio = label.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        };
    });

    modalOpen('statusModal');
}

// Confirm button handler for status modal
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('confirmStatusBtn');
    if (btn) {
        btn.addEventListener('click', async () => {
            const selected = document.querySelector('input[name="projStatus"]:checked');
            if (!selected) {
                toast('Please select a status', 'warning');
                return;
            }
            if (selected.value === project.status) {
                toast('This is already the current status', 'warning');
                return;
            }

            btn.disabled = true;
            const originalText = btn.textContent;
            btn.textContent = 'Updating...';

            try {
                await api.updateProjectStatus(projectId, selected.value);
                toast('Project status updated successfully', 'success');
                modalClose('statusModal');
                loadProject();
            } catch (err) {
                toast(err.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        });
    }
});

// ============================================================
// Edit / Delete project
// ============================================================
function editProject() {
    const name = prompt('Project name:', project.name);
    if (name === null || !name.trim()) return;
    const desc = prompt('Description:', project.description || '');
    if (desc === null) return;
    api.updateProject(projectId, { name: name.trim(), description: desc })
        .then(() => { toast('Project updated', 'success'); loadProject(); })
        .catch(err => toast(err.message, 'error'));
}

async function deleteProject() {
    if (!confirmDialog(
        `Are you sure you want to delete "${project.name}"?\n` +
        `This will archive the project.`
    )) return;
    try {
        await api.deleteProject(projectId);
        toast('Project deleted', 'success');
        setTimeout(() => window.location.href = 'projects.html', 700);
    } catch (err) {
        toast(err.message, 'error');
    }
}

// ============================================================
// Tasks
// ============================================================
async function loadTasks(page = 1) {
    currentTasksPage = page;
    const list = document.getElementById('tasksList');
    showLoader(list);
    const params = { page, page_size: 10 };
    const status = document.getElementById('taskStatusFilter').value;
    const priority = document.getElementById('taskPriorityFilter').value;
    if (status) params.task_status = status;
    if (priority) params.priority = priority;
    try {
        const res = await api.getTasks(projectId, params);
        if (!res.items || res.items.length === 0) {
            list.innerHTML = `<div class="empty"><div class="empty-icon">✅</div>No tasks yet</div>`;
            document.getElementById('tasksPagination').innerHTML = '';
            return;
        }
        list.innerHTML = `<div class="grid">${res.items.map(taskCard).join('')}</div>`;

        list.querySelectorAll('[data-task-id]').forEach(el => {
            const taskId = el.dataset.taskId;
            const taskObj = res.items.find(t => String(t.id) === String(taskId));

            el.querySelector('.task-open')?.addEventListener('click', () => {
                window.location.href = `task.html?project_id=${projectId}&id=${taskId}`;
            });

            el.querySelector('.task-edit')?.addEventListener('click', () => openTaskModal(taskObj));

            el.querySelector('.task-delete')?.addEventListener('click', () => deleteTask(taskId));

            el.querySelector('.task-status')?.addEventListener('click', () => {
                // ارسال title و status فعلی
                quickChangeStatus(taskObj.id, taskObj.title, taskObj.status);
            });
        });

        renderPagination(document.getElementById('tasksPagination'), res.page, res.pages, loadTasks);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

function taskCard(t) {
    return `
    <div class="project-card" data-task-id="${t.id}">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:8px;">
        <h3>${escapeHtml(t.title)}</h3>
        <div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end;">
          ${statusBadge(t.status)}
          ${priorityBadge(t.priority)}
        </div>
      </div>
      <p class="desc">${escapeHtml(t.description || 'No description')}</p>
      <div style="font-size:12px;color:var(--gray-500);">Due: ${fmtDateShort(t.due_date)}</div>
      <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;">
        <button class="btn btn-secondary btn-xs task-open">Open</button>
        <button class="btn btn-secondary btn-xs task-status">Status</button>
        <button class="btn btn-secondary btn-xs task-edit">Edit</button>
        <button class="btn btn-danger btn-xs task-delete">Delete</button>
      </div>
    </div>
  `;
}

// ============================================================
// Quick change task status (with proper UI)
// ============================================================
let statusChangeTaskId = null;
let statusChangeTaskTitle = '';

function quickChangeStatus(taskId, taskTitle, currentStatus) {
    statusChangeTaskId = taskId;
    statusChangeTaskTitle = taskTitle || '';

    // عنوان و وضعیت فعلی
    document.getElementById('taskStatusTaskTitle').textContent = statusChangeTaskTitle;
    document.getElementById('taskCurrentStatusBadge').innerHTML =
        statusBadge(currentStatus);

    // ریست انتخاب‌ها
    const labels = document.querySelectorAll('#taskStatusOptions .status-option');
    labels.forEach(l => l.classList.remove('selected', 'disabled'));

    const radios = document.querySelectorAll('input[name="taskStatusRadio"]');
    radios.forEach(r => {
        r.checked = false;
        if (r.value === currentStatus) {
            r.closest('.status-option').classList.add('disabled');
        }
    });

    // هندل کلیک روی گزینه‌ها
    labels.forEach(label => {
        label.onclick = () => {
            if (label.classList.contains('disabled')) return;
            labels.forEach(l => l.classList.remove('selected'));
            label.classList.add('selected');
            const radio = label.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        };
    });

    modalOpen('taskStatusModal');
}

// Confirm button handler — در DOMContentLoaded ثبت می‌شه
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('confirmTaskStatusBtn');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        const selected = document.querySelector('input[name="taskStatusRadio"]:checked');
        if (!selected) {
            toast('Please select a status', 'warning');
            return;
        }

        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = 'Updating...';

        try {
            await api.updateTaskStatus(projectId, statusChangeTaskId, selected.value);
            toast('Task status updated successfully', 'success');
            modalClose('taskStatusModal');
            loadTasks(currentTasksPage);
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
});

async function deleteTask(taskId) {
    if (!confirmDialog('Delete this task?')) return;
    try {
        await api.deleteTask(projectId, taskId);
        toast('Task deleted', 'success');
        loadTasks(currentTasksPage);
    } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('taskStatusFilter').addEventListener('change', () => loadTasks(1));
document.getElementById('taskPriorityFilter').addEventListener('change', () => loadTasks(1));

// ============================================================
// Task modal (create / edit)
// ============================================================
let editingTaskId = null;

document.getElementById('newTaskBtn').addEventListener('click', () => openTaskModal(null));

async function openTaskModal(task) {
    editingTaskId = task ? task.id : null;
    document.getElementById('taskModalTitle').textContent = task ? 'Edit Task' : 'New Task';
    document.getElementById('taskId').value = task?.id || '';
    document.getElementById('taskTitle').value = task?.title || '';
    document.getElementById('taskDesc').value = task?.description || '';
    document.getElementById('taskPriority').value = task?.priority || '';
    document.getElementById('taskStatus').value = task?.status || '';
    document.getElementById('taskDeps').value = '';
    document.getElementById('taskDueValue').value = '';
    document.getElementById('taskDueUnit').value = '';

    // بارگذاری لیست اعضا و تگ‌های پروژه
    await loadAssigneesAndTags();

    // در حالت edit، مقادیر قبلی رو انتخاب کن
    if (task) {
        // assignees
        try {
            const taskDetail = await api.getTask(projectId, task.id);
            if (taskDetail.assignees && Array.isArray(taskDetail.assignees)) {
                const assigneeIds = taskDetail.assignees.map(a => a.id || a);
                Array.from(document.getElementById('taskAssignees').options).forEach(opt => {
                    if (assigneeIds.includes(parseInt(opt.value))) opt.selected = true;
                });
            }
        } catch (e) { /* ignore */ }

        // tags
        try {
            const tags = await api.getTaskTags(projectId, task.id);
            const tagIds = (tags || []).map(t => t.id);
            Array.from(document.getElementById('taskTags').options).forEach(opt => {
                if (tagIds.includes(parseInt(opt.value))) opt.selected = true;
            });
        } catch (e) { /* ignore */ }

        // dependencies
        try {
            const deps = await api.getDependencies(projectId, task.id, { page: 1, page_size: 100 });
            const depIds = (deps.items || []).map(d => d.id);
            document.getElementById('taskDeps').value = depIds.join(',');
        } catch (e) { /* ignore */ }
    }

    modalOpen('taskModal');
}

async function loadAssigneesAndTags() {
    const assigneeSel = document.getElementById('taskAssignees');
    assigneeSel.innerHTML = members.map(m =>
        `<option value="${m.user_id}">${escapeHtml(m.username || ('User #' + m.user_id))} (${m.role})</option>`
    ).join('');

    const tagSel = document.getElementById('taskTags');
    tagSel.innerHTML = allTags.map(t =>
        `<option value="${t.id}">${escapeHtml(t.name)} [${t.scope}]</option>`
    ).join('');
}

// ============================================================
// Task form submit
// ============================================================
document.getElementById('taskForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('taskSubmitBtn');
    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = 'Saving...';

    try {
        // ===== مقادیر پایه =====
        const title = document.getElementById('taskTitle').value.trim();
        const description = document.getElementById('taskDesc').value.trim() || null;
        const priority = document.getElementById('taskPriority').value || null;

        // ===== Due date =====
        const dueValueRaw = document.getElementById('taskDueValue').value.trim();
        const dueUnit = document.getElementById('taskDueUnit').value || null;

        // ===== آرایه‌ها — همیشه آرایه، حتی اگه خالی =====
        const tags_id = getSelectedIds('taskTags');           // []
        const assignee_ids = getSelectedIds('taskAssignees'); // []
        const dependency_ids = parseIdsString(                // []
            document.getElementById('taskDeps').value
        );

        // اعتبارسنجی due_value / due_unit
        if ((dueValueRaw && !dueUnit) || (!dueValueRaw && dueUnit)) {
            toast('Both "due_value" and "due_unit" must be provided together', 'warning');
            btn.disabled = false;
            btn.textContent = originalText;
            return;
        }

        // ===== ساخت payload مطابق schema =====
        const payload = {
            title,
            description,
            priority,
            tags_id,
            assignee_ids,
            dependency_ids,
        };

        if (dueValueRaw && dueUnit) {
            payload.due_value = parseInt(dueValueRaw, 10);
            payload.due_unit = dueUnit;
        }

        // ===== حالت Edit =====
        if (editingTaskId) {
            const updatePayload = {
                title,
                description,
                priority,
                assignee_ids,
                dependency_ids,
            };
            if (payload.due_value !== undefined) {
                updatePayload.due_value = payload.due_value;
                updatePayload.due_unit = payload.due_unit;
            }

            await api.updateTask(projectId, editingTaskId, updatePayload);

            const newStatus = document.getElementById('taskStatus').value;
            if (newStatus) {
                try {
                    await api.updateTaskStatus(projectId, editingTaskId, newStatus);
                } catch (e) { /* ignore */ }
            }

            if (tags_id.length > 0) {
                try {
                    await api.addTagsToTask(projectId, editingTaskId, tags_id);
                } catch (e) { /* ignore */ }
            }

            toast('Task updated successfully', 'success');
        }

        // ===== حالت Create =====
        else {
            const result = await api.createTask(projectId, payload);
            toast(`Task created (ID: ${result.task_id})`, 'success');
        }

        modalClose('taskModal');
        document.getElementById('taskForm').reset();
        loadTasks(currentTasksPage);
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
});

// ============================================================
// Members
// ============================================================
async function loadMembers(page = 1) {
    currentMembersPage = page;
    const list = document.getElementById('membersList');
    showLoader(list);
    try {
        const res = await api.getMembers(projectId, { page, page_size: 10 });
        members = res.items || [];
        if (members.length === 0) {
            list.innerHTML = `<div class="empty">No members</div>`;
            return;
        }
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>User</th><th>Role</th><th>Actions</th></tr></thead>
          <tbody>
            ${members.map(m => `
              <tr>
                <td>${m.user_id}</td>
                <td>${escapeHtml(m.username || ('#' + m.user_id))}</td>
                <td>${roleBadge(m.role)}</td>
                <td>
                  <button class="btn btn-secondary btn-xs" data-action="role" data-user="${m.user_id}" data-role="${m.role}">Change Role</button>
                  <button class="btn btn-danger btn-xs" data-action="remove" data-user="${m.user_id}">Remove</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="role"]').forEach(b => {
            b.addEventListener('click', () => changeRole(b.dataset.user, b.dataset.role));
        });
        list.querySelectorAll('[data-action="remove"]').forEach(b => {
            b.addEventListener('click', () => removeMember(b.dataset.user));
        });
        renderPagination(document.getElementById('membersPagination'), res.page, res.pages, loadMembers);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

async function changeRole(userId, currentRole) {
    const role = prompt('New role (owner/manager/member/viewer):', currentRole);
    if (!role) return;
    if (!['owner', 'manager', 'member', 'viewer'].includes(role)) {
        return toast('Invalid role', 'error');
    }
    try {
        await api.updateMember(projectId, userId, role);
        toast('Role updated', 'success');
        loadMembers(currentMembersPage);
    } catch (err) { toast(err.message, 'error'); }
}

async function removeMember(userId) {
    if (!confirmDialog('Remove this member?')) return;
    try {
        await api.removeMember(projectId, userId);
        toast('Member removed', 'success');
        loadMembers(currentMembersPage);
    } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('addMemberBtn').addEventListener('click', () => modalOpen('memberModal'));

document.getElementById('memberForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        await api.addMember(projectId, {
            user_id: parseInt(document.getElementById('memberUserId').value),
            role: document.getElementById('memberRole').value,
        });
        toast('Member added', 'success');
        modalClose('memberModal');
        document.getElementById('memberForm').reset();
        loadMembers(1);
    } catch (err) { toast(err.message, 'error'); }
});

// ============================================================
// Tags
// ============================================================
async function loadTags(page = 1) {
    currentTagsPage = page;
    const list = document.getElementById('tagsList');
    showLoader(list);
    try {
        const res = await api.getProjectTags(projectId, { page, page_size: 20 });
        allTags = res.items || [];
        if (allTags.length === 0) {
            list.innerHTML = `<div class="empty">No tags yet</div>`;
            return;
        }
        list.innerHTML = `
      <div class="table-wrapper">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Scope</th><th>Actions</th></tr></thead>
          <tbody>
            ${allTags.map(t => `
              <tr>
                <td>${t.id}</td>
                <td>${escapeHtml(t.name)}</td>
                <td>${badge(t.scope, t.scope)}</td>
                <td>
                  <button class="btn btn-secondary btn-xs" data-action="edit" data-id="${t.id}" data-name="${escapeHtml(t.name)}">Edit</button>
                  <button class="btn btn-danger btn-xs" data-action="del" data-id="${t.id}">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
        list.querySelectorAll('[data-action="edit"]').forEach(b => {
            b.addEventListener('click', () => openTagModal(b.dataset.id, b.dataset.name));
        });
        list.querySelectorAll('[data-action="del"]').forEach(b => {
            b.addEventListener('click', () => deleteTag(b.dataset.id));
        });
        renderPagination(document.getElementById('tagsPagination'), res.page, res.pages, loadTags);
    } catch (err) {
        list.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
}

document.getElementById('newTagBtn').addEventListener('click', () => openTagModal(null, ''));

function openTagModal(id, name) {
    document.getElementById('tagId').value = id || '';
    document.getElementById('tagName').value = name || '';
    document.getElementById('tagModalTitle').textContent = id ? 'Edit Tag' : 'New Tag';
    modalOpen('tagModal');
}

document.getElementById('tagForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('tagId').value;
    const name = document.getElementById('tagName').value.trim();
    try {
        if (id) {
            await api.updateProjectTag(projectId, id, { name });
            toast('Tag updated', 'success');
        } else {
            await api.createProjectTag(projectId, { name });
            toast('Tag created', 'success');
        }
        modalClose('tagModal');
        loadTags(currentTagsPage);
    } catch (err) { toast(err.message, 'error'); }
});

async function deleteTag(id) {
    if (!confirmDialog('Delete tag?')) return;
    try {
        await api.deleteProjectTag(projectId, id);
        toast('Tag deleted', 'success');
        loadTags(currentTagsPage);
    } catch (err) { toast(err.message, 'error'); }
}

// ============================================================
// Init
// ============================================================
loadProject();