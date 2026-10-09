let CURRENT_USER = null;

function setupTabs() {
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
  });
}

// ---------- Productos ----------

async function loadProducts() {
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

async function loadUsers() {
  const tbody = document.getElementById('user-table-body');
  tbody.innerHTML = '<tr><td colspan="5">Cargando...</td></tr>';
  try {
    const users = await apiFetch('/api/v1/users?limit=500');
    tbody.innerHTML = users
      .map((u) => {
        const isSelf = CURRENT_USER && u.id === CURRENT_USER.id;
        const nextRole = u.role === 'admin' ? 'customer' : 'admin';
        const actionLabel = u.role === 'admin' ? 'Quitar admin' : 'Hacer admin';
        return `
        <tr>
          <td>${u.id}</td>
          <td>${u.email}</td>
          <td>${u.full_name || '-'}</td>
          <td>${u.role}</td>
          <td>
            ${isSelf
              ? '<span class="muted">(tú)</span>'
              : `<button class="btn-small role-btn" data-id="${u.id}" data-role="${nextRole}">${actionLabel}</button>`}
          </td>
        </tr>`;
      })
      .join('');
    tbody.querySelectorAll('.role-btn').forEach((btn) => {
      btn.addEventListener('click', () => changeRole(btn.dataset.id, btn.dataset.role));
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="error">${err.message}</td></tr>`;
  }
}

function setupUserForm() {
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

async function changeRole(userId, role) {
  if (!confirm(`¿Cambiar el rol de este usuario a "${role}"?`)) return;
  try {
    await apiFetch(`/api/v1/users/${userId}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    });
    loadUsers();
  } catch (err) {
    alert(err.message);
  }
}

// ---------- Encuestas ----------

function renderStatTile(label, value) {
  return `<div class="stat-tile"><div class="stat-value">${value}</div><div class="stat-label">${label}</div></div>`;
}

async function loadSurveys() {
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

  if (CURRENT_USER.role !== 'admin') {
    guard.textContent = 'No tienes permisos de administrador para ver esta página.';
    return;
  }

  guard.classList.add('hidden');
  content.classList.remove('hidden');

  setupTabs();
  setupProductForm();
  setupUserForm();
  loadProducts();
  loadUsers();
  loadSurveys();
});
