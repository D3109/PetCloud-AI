let CURRENT_USER = null;

const ROLE_LABELS = {
  root: 'Super administrador (ROOT)',
  admin: 'Administrador',
  gestor_productos: 'Gestor de productos',
  atencion_cliente: 'Atención al cliente',
  customer: 'Cliente',
};

// Qué pestañas puede ver cada rol. root y admin ven todo.
const TAB_ACCESS = {
  root: ['dashboard', 'productos', 'usuarios', 'encuestas', 'auditoria'],
  admin: ['dashboard', 'productos', 'usuarios', 'encuestas', 'auditoria'],
  gestor_productos: ['productos'],
  atencion_cliente: ['encuestas'],
};

function canSeeTab(tab) {
  const allowed = TAB_ACCESS[CURRENT_USER.role] || [];
  return allowed.includes(tab);
}

function setupTabs() {
  const tabButtons = Array.from(document.querySelectorAll('.tab-btn'));
  let firstVisible = null;
  tabButtons.forEach((btn) => {
    const tab = btn.dataset.tab;
    if (!canSeeTab(tab)) {
      btn.classList.add('hidden');
      document.getElementById(`tab-${tab}`).classList.remove('active');
      document.getElementById(`tab-${tab}`).classList.add('hidden');
      return;
    }
    if (!firstVisible) firstVisible = tab;
    btn.addEventListener('click', () => {
      tabButtons.forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${tab}`).classList.add('active');
    });
  });

  // Activa la primera pestaña visible para este rol.
  tabButtons.forEach((b) => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
  if (firstVisible) {
    document.querySelector(`.tab-btn[data-tab="${firstVisible}"]`).classList.add('active');
    document.getElementById(`tab-${firstVisible}`).classList.add('active');
  }
}

// ---------- Dashboard ----------

function renderStatTile(label, value) {
  return `<div class="stat-tile"><div class="stat-value">${value}</div><div class="stat-label">${label}</div></div>`;
}

function renderAuditRows(entries) {
  if (entries.length === 0) {
    return '<tr><td colspan="5">Sin actividad registrada todavía.</td></tr>';
  }
  return entries
    .map(
      (a) => `
      <tr>
        <td>${new Date(a.created_at).toLocaleString('es-CO')}</td>
        <td>${a.actor_email || 'sistema'}</td>
        <td>${a.action}</td>
        <td>${a.entity_type}${a.entity_id ? ' #' + a.entity_id : ''}</td>
        <td>${a.detail || '-'}</td>
      </tr>`
    )
    .join('');
}

async function loadDashboard() {
  if (!canSeeTab('dashboard')) return;
  const statsBox = document.getElementById('dashboard-stats');
  const ordersBox = document.getElementById('dashboard-orders');
  const auditBody = document.getElementById('dashboard-audit-body');
  statsBox.innerHTML = 'Cargando...';
  try {
    const d = await apiFetch('/api/v1/admin/dashboard');
    statsBox.innerHTML = [
      renderStatTile('Usuarios totales', d.total_users),
      renderStatTile('Usuarios activos', d.active_users),
      renderStatTile('Usuarios bloqueados', d.blocked_users),
      renderStatTile('Productos activos', d.products_active),
      renderStatTile('Productos inactivos', d.products_inactive),
      renderStatTile('Stock bajo', d.low_stock_count),
      renderStatTile('Ventas totales', `$${Number(d.total_sales).toLocaleString('es-CO')}`),
      renderStatTile('Respuestas encuesta', d.survey_total_respuestas),
      renderStatTile('Satisfacción prom.', d.survey_promedio_satisfaccion),
    ].join('');

    const statusLabels = { pending: 'Pendientes', paid: 'Pagados' };
    const orderEntries = Object.entries(d.orders_by_status);
    ordersBox.innerHTML =
      orderEntries.length === 0
        ? '<p class="muted">Aún no hay pedidos.</p>'
        : orderEntries
            .map(([status, count]) => renderStatTile(statusLabels[status] || status, count))
            .join('');

    auditBody.innerHTML = renderAuditRows(d.recent_audit);
  } catch (err) {
    statsBox.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

// ---------- Auditoría (listado completo) ----------

async function loadAuditLog() {
  if (!canSeeTab('auditoria')) return;
  const tbody = document.getElementById('audit-table-body');
  tbody.innerHTML = '<tr><td colspan="6">Cargando...</td></tr>';
  try {
    const entries = await apiFetch('/api/v1/audit?limit=200');
    if (entries.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6">Sin actividad registrada todavía.</td></tr>';
      return;
    }
    tbody.innerHTML = entries
      .map(
        (a) => `
        <tr>
          <td>${new Date(a.created_at).toLocaleString('es-CO')}</td>
          <td>${a.actor_email || 'sistema'}</td>
          <td>${a.action}</td>
          <td>${a.entity_type}</td>
          <td>${a.entity_id ?? '-'}</td>
          <td>${a.detail || '-'}</td>
        </tr>`
      )
      .join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="error">${err.message}</td></tr>`;
  }
}

// ---------- Productos ----------

async function loadProducts() {
  if (!canSeeTab('productos')) return;
  const tbody = document.getElementById('product-table-body');
  tbody.innerHTML = '<tr><td colspan="6">Cargando...</td></tr>';
  try {
    const products = await apiFetch('/api/v1/products?include_inactive=true&limit=500');
    if (products.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6">No hay productos todavía.</td></tr>';
      return;
    }
    tbody.innerHTML = products
      .map(
        (p) => `
        <tr data-id="${p.id}">
          <td>${p.id}</td>
          <td>${p.name}</td>
          <td>${p.sku}</td>
          <td>$${Number(p.price).toLocaleString('es-CO')}</td>
          <td>${p.is_active ? 'Activo' : 'Inactivo'}</td>
          <td>
            ${p.is_active ? `<button class="btn-small deactivate-btn" data-id="${p.id}">Desactivar</button>` : ''}
          </td>
        </tr>`
      )
      .join('');
    tbody.querySelectorAll('.deactivate-btn').forEach((btn) => {
      btn.addEventListener('click', () => deactivateProduct(btn.dataset.id));
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="error">${err.message}</td></tr>`;
  }
}

async function deactivateProduct(id) {
  if (!confirm('¿Desactivar este producto? Dejará de verse en el catálogo.')) return;
  try {
    await apiFetch(`/api/v1/products/${id}`, { method: 'DELETE' });
    loadProducts();
  } catch (err) {
    alert(err.message);
  }
}

function setupProductForm() {
  if (!canSeeTab('productos')) return;
  const form = document.getElementById('product-form');
  const errorBox = document.getElementById('product-error');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.textContent = '';
    const name = document.getElementById('p-name').value.trim();
    const sku = document.getElementById('p-sku').value.trim();
    const price = document.getElementById('p-price').value;
    const description = document.getElementById('p-description').value.trim();
    const imageUrl = document.getElementById('p-image-url').value.trim();
    try {
      await apiFetch('/api/v1/products', {
        method: 'POST',
        body: JSON.stringify({
          name,
          sku,
          price,
          description: description || null,
          image_url: imageUrl || null,
        }),
      });
      form.reset();
      loadProducts();
    } catch (err) {
      errorBox.textContent = err.message;
    }
  });
}

// ---------- Usuarios ----------

function assignableRoleOptions() {
  // Un admin normal no puede crear ni ascender a otro admin; solo root puede.
  if (CURRENT_USER.role === 'root') {
    return ['customer', 'atencion_cliente', 'gestor_productos', 'admin'];
  }
  return ['customer', 'atencion_cliente', 'gestor_productos'];
}

function setupRoleSelectOptions() {
  const select = document.getElementById('u-role');
  const allowed = assignableRoleOptions();
  Array.from(select.options).forEach((opt) => {
    if (!allowed.includes(opt.value)) opt.remove();
  });
}

async function loadUsers() {
  if (!canSeeTab('usuarios')) return;
  const tbody = document.getElementById('user-table-body');
  tbody.innerHTML = '<tr><td colspan="6">Cargando...</td></tr>';
  try {
    const users = await apiFetch('/api/v1/users?limit=500');
    const allowedRoles = assignableRoleOptions();
    tbody.innerHTML = users
      .map((u) => {
        const isSelf = CURRENT_USER && u.id === CURRENT_USER.id;
        const isRoot = u.role === 'root';
        const roleOptions = allowedRoles
          .map((r) => `<option value="${r}" ${r === u.role ? 'selected' : ''}>${ROLE_LABELS[r]}</option>`)
          .join('');
        const canManage = !isSelf && !isRoot;
        return `
        <tr>
          <td>${u.id}</td>
          <td>${u.email}</td>
          <td>${u.full_name || '-'}</td>
          <td>
            ${canManage
              ? `<select class="role-select" data-id="${u.id}">${roleOptions}</select>`
              : ROLE_LABELS[u.role] || u.role}
          </td>
          <td>${u.is_active ? 'Activo' : 'Bloqueado'}</td>
          <td>
            ${isSelf ? '<span class="muted">(tú)</span>' : ''}
            ${isRoot && !isSelf ? '<span class="muted">(protegido)</span>' : ''}
            ${canManage
              ? `<button class="btn-small toggle-active-btn" data-id="${u.id}" data-active="${u.is_active}">
                   ${u.is_active ? 'Bloquear' : 'Activar'}
                 </button>`
              : ''}
          </td>
        </tr>`;
      })
      .join('');
    tbody.querySelectorAll('.role-select').forEach((select) => {
      select.addEventListener('change', () => changeRole(select.dataset.id, select.value));
    });
    tbody.querySelectorAll('.toggle-active-btn').forEach((btn) => {
      btn.addEventListener('click', () =>
        toggleActive(btn.dataset.id, btn.dataset.active === '1' || btn.dataset.active === 'true')
      );
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="error">${err.message}</td></tr>`;
  }
}

async function changeRole(userId, role) {
  if (!confirm(`¿Cambiar el rol de este usuario a "${ROLE_LABELS[role] || role}"?`)) {
    loadUsers();
    return;
  }
  try {
    await apiFetch(`/api/v1/users/${userId}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
    loadUsers();
  } catch (err) {
    alert(err.message);
    loadUsers();
  }
}

async function toggleActive(userId, currentlyActive) {
  const action = currentlyActive ? 'bloquear' : 'activar';
  if (!confirm(`¿Quieres ${action} esta cuenta?`)) return;
  try {
    await apiFetch(`/api/v1/users/${userId}/active`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !currentlyActive }),
    });
    loadUsers();
  } catch (err) {
    alert(err.message);
  }
}

function setupUserForm() {
  if (!canSeeTab('usuarios')) return;
  setupRoleSelectOptions();
  const form = document.getElementById('user-form');
  const errorBox = document.getElementById('user-form-error');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.textContent = '';
    const email = document.getElementById('u-email').value.trim();
    const password = document.getElementById('u-password').value;
    const fullName = document.getElementById('u-fullname').value.trim();
    const role = document.getElementById('u-role').value;
    try {
      await apiFetch('/api/v1/users/admin', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          full_name: fullName || null,
          role,
        }),
      });
      form.reset();
      loadUsers();
    } catch (err) {
      errorBox.textContent = err.message;
    }
  });
}

// ---------- Encuestas ----------

async function loadSurveys() {
  if (!canSeeTab('encuestas')) return;
  const statsBox = document.getElementById('survey-stats');
  const tbody = document.getElementById('survey-table-body');
  statsBox.innerHTML = 'Cargando...';
  tbody.innerHTML = '<tr><td colspan="9">Cargando...</td></tr>';
  try {
    const stats = await apiFetch('/api/v1/surveys/stats');
    statsBox.innerHTML = [
      renderStatTile('Respuestas', stats.total_respuestas),
      renderStatTile('Precisión recomendación', stats.promedio_precision_recomendacion),
      renderStatTile('Facilidad de uso', stats.promedio_facilidad_uso),
      renderStatTile('Confianza', stats.promedio_confianza_usuario),
      renderStatTile('Satisfacción', stats.promedio_nivel_satisfaccion),
      renderStatTile('Seguridad', stats.promedio_percepcion_seguridad),
      renderStatTile('Intención recompra', stats.promedio_intencion_recompra),
    ].join('');

    const surveys = await apiFetch('/api/v1/surveys?limit=200');
    if (surveys.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9">Aún no hay respuestas.</td></tr>';
      return;
    }
    tbody.innerHTML = surveys
      .map(
        (s) => `
        <tr>
          <td>${new Date(s.created_at).toLocaleDateString('es-CO')}</td>
          <td>#${s.user_id}</td>
          <td>${s.precision_recomendacion}</td>
          <td>${s.facilidad_uso}</td>
          <td>${s.confianza_usuario}</td>
          <td>${s.nivel_satisfaccion}</td>
          <td>${s.percepcion_seguridad}</td>
          <td>${s.intencion_recompra}</td>
          <td>${s.comentario || '-'}</td>
        </tr>`
      )
      .join('');
  } catch (err) {
    statsBox.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

// ---------- Bootstrap ----------

const STAFF_ROLES = ['root', 'admin', 'gestor_productos', 'atencion_cliente'];

document.addEventListener('DOMContentLoaded', async () => {
  const guard = document.getElementById('admin-guard');
  const content = document.getElementById('admin-content');

  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }

  try {
    CURRENT_USER = await apiFetch('/api/v1/auth/me');
  } catch (err) {
    window.location.href = 'login.html';
    return;
  }

  if (!STAFF_ROLES.includes(CURRENT_USER.role)) {
    guard.textContent = 'No tienes permisos de administrador para ver esta página.';
    return;
  }

  guard.classList.add('hidden');
  content.classList.remove('hidden');
  document.getElementById('role-badge').textContent =
    `Conectado como ${CURRENT_USER.email} — ${ROLE_LABELS[CURRENT_USER.role] || CURRENT_USER.role}`;

  setupTabs();
  setupProductForm();
  setupUserForm();
  loadDashboard();
  loadProducts();
  loadUsers();
  loadSurveys();
  loadAuditLog();
});
