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
  root: ['dashboard', 'productos', 'usuarios', 'pedidos', 'encuestas', 'auditoria'],
  admin: ['dashboard', 'productos', 'usuarios', 'pedidos', 'encuestas', 'auditoria'],
  gestor_productos: ['productos'],
  atencion_cliente: ['pedidos', 'encuestas'],
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

function renderRecentSurveys(surveys) {
  if (!surveys || surveys.length === 0) {
    return '<p class="muted">Aún no hay encuestas respondidas.</p>';
  }
  return surveys
    .map(
      (s) => `
      <div class="survey-mini-card">
        <span class="survey-mini-stars">${'★'.repeat(s.nivel_satisfaccion)}${'☆'.repeat(5 - s.nivel_satisfaccion)}</span>
        <span class="muted">${s.order_id ? `Pedido #${s.order_id} · ` : ''}${new Date(s.created_at).toLocaleDateString('es-CO')}</span>
        ${s.comentario ? `<p>"${s.comentario}"</p>` : ''}
      </div>`
    )
    .join('');
}

async function loadDashboard() {
  if (!canSeeTab('dashboard')) return;
  const statsBox = document.getElementById('dashboard-stats');
  const ordersBox = document.getElementById('dashboard-orders');
  const surveysBox = document.getElementById('dashboard-surveys');
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

    surveysBox.innerHTML = renderRecentSurveys(d.recent_surveys);
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

async function loadProductCategoryOptions() {
  const select = document.getElementById('p-category');
  if (!select || select.dataset.populated) return;
  try {
    const categories = await apiFetch('/api/v1/categories');
    categories
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((c) => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name;
        select.appendChild(opt);
      });
    select.dataset.populated = 'true';
  } catch (err) {
    // si falla, el select simplemente queda sin opciones; no bloquea el formulario
  }
}

async function loadProducts() {
  if (!canSeeTab('productos')) return;
  const tbody = document.getElementById('product-table-body');
  tbody.innerHTML = '<tr><td colspan="10">Cargando...</td></tr>';
  try {
    const products = await apiFetch('/api/v1/products?include_inactive=true&limit=500');
    if (products.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10">No hay productos todavía.</td></tr>';
      return;
    }
    const petTypeLabels = { perro: 'Perro', gato: 'Gato', ambas: 'Ambas', otro: 'Otro' };
    tbody.innerHTML = products
      .map(
        (p) => `
        <tr data-id="${p.id}">
          <td>${p.id}</td>
          <td>${p.name}</td>
          <td>${p.sku}</td>
          <td>${p.brand || '-'}</td>
          <td>${petTypeLabels[p.pet_type] || '-'}</td>
          <td>$${Number(p.price).toLocaleString('es-CO')}</td>
          <td>
            <span class="stock-cell" data-id="${p.id}">${p.stock_quantity ?? 0}</span>
            <button class="btn-small stock-adjust-btn" data-id="${p.id}" title="Ajustar existencias">✎</button>
          </td>
          <td>${p.is_active ? 'Activo' : 'Inactivo'}</td>
          <td>${p.updated_at ? new Date(p.updated_at).toLocaleDateString('es-CO') : '-'}</td>
          <td>
            <button class="btn-small edit-product-btn" data-id="${p.id}">Editar</button>
            ${p.is_active ? `<button class="btn-small deactivate-btn" data-id="${p.id}">Desactivar</button>` : ''}
          </td>
        </tr>`
      )
      .join('');
    LOADED_PRODUCTS_BY_ID = Object.fromEntries(products.map((p) => [p.id, p]));
    tbody.querySelectorAll('.deactivate-btn').forEach((btn) => {
      btn.addEventListener('click', () => deactivateProduct(btn.dataset.id));
    });
    tbody.querySelectorAll('.stock-adjust-btn').forEach((btn) => {
      btn.addEventListener('click', () => adjustProductStock(btn.dataset.id));
    });
    tbody.querySelectorAll('.edit-product-btn').forEach((btn) => {
      btn.addEventListener('click', () => startEditProduct(btn.dataset.id));
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="10" class="error">${err.message}</td></tr>`;
  }
}

let LOADED_PRODUCTS_BY_ID = {};
let EDITING_PRODUCT_ID = null;

function startEditProduct(id) {
  const product = LOADED_PRODUCTS_BY_ID[id];
  if (!product) return;
  EDITING_PRODUCT_ID = Number(id);

  document.getElementById('p-name').value = product.name || '';
  document.getElementById('p-sku').value = product.sku || '';
  document.getElementById('p-sku').disabled = true;
  document.getElementById('p-price').value = product.price;
  document.getElementById('p-description').value = product.description || '';
  document.getElementById('p-image-url').value = product.image_url || '';
  document.getElementById('p-brand').value = product.brand || '';
  document.getElementById('p-pet-type').value = product.pet_type || '';
  document.getElementById('p-category').value =
    product.categories && product.categories.length ? product.categories[0].id : '';
  document.getElementById('p-stock').value = product.stock_quantity ?? 0;
  document.getElementById('p-stock').disabled = true; // el stock se ajusta desde la tabla, no aqui

  document.getElementById('product-form-title').textContent = `Editando: ${product.name}`;
  document.getElementById('product-form-submit').textContent = 'Guardar cambios';
  document.getElementById('product-form-cancel').classList.remove('hidden');
  document.getElementById('product-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function cancelEditProduct() {
  EDITING_PRODUCT_ID = null;
  const form = document.getElementById('product-form');
  form.reset();
  document.getElementById('p-sku').disabled = false;
  document.getElementById('p-stock').disabled = false;
  document.getElementById('product-form-title').textContent = 'Crear producto';
  document.getElementById('product-form-submit').textContent = 'Crear';
  document.getElementById('product-form-cancel').classList.add('hidden');
}

async function adjustProductStock(productId) {
  const current = document.querySelector(`.stock-cell[data-id="${productId}"]`)?.textContent || '0';
  const input = prompt(
    `Existencias actuales: ${current}.\nEscribe cuánto quieres sumar (positivo) o restar (negativo):`,
    '0'
  );
  if (input === null) return;
  const delta = Number(input);
  if (!Number.isInteger(delta) || delta === 0) {
    alert('Ingresa un número entero distinto de 0.');
    return;
  }
  try {
    await apiFetch(`/api/v1/inventory/${productId}/adjust`, {
      method: 'PUT',
      body: JSON.stringify({ delta }),
    });
    loadProducts();
  } catch (err) {
    alert(err.message);
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
  loadProductCategoryOptions();
  const form = document.getElementById('product-form');
  const errorBox = document.getElementById('product-error');
  document.getElementById('product-form-cancel')?.addEventListener('click', cancelEditProduct);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.textContent = '';
    const name = document.getElementById('p-name').value.trim();
    const sku = document.getElementById('p-sku').value.trim();
    const price = document.getElementById('p-price').value;
    const description = document.getElementById('p-description').value.trim();
    const imageUrl = document.getElementById('p-image-url').value.trim();
    const brand = document.getElementById('p-brand').value.trim();
    const petType = document.getElementById('p-pet-type').value;
    const categoryId = document.getElementById('p-category').value;
    const initialStock = Number(document.getElementById('p-stock').value || 0);

    try {
      if (EDITING_PRODUCT_ID) {
        await apiFetch(`/api/v1/products/${EDITING_PRODUCT_ID}`, {
          method: 'PUT',
          body: JSON.stringify({
            name,
            price,
            description: description || null,
            image_url: imageUrl || null,
            brand: brand || null,
            pet_type: petType || null,
            category_ids: categoryId ? [Number(categoryId)] : [],
          }),
        });
        cancelEditProduct();
      } else {
        const product = await apiFetch('/api/v1/products', {
          method: 'POST',
          body: JSON.stringify({
            name,
            sku,
            price,
            description: description || null,
            image_url: imageUrl || null,
            brand: brand || null,
            pet_type: petType || null,
            category_ids: categoryId ? [Number(categoryId)] : [],
          }),
        });
        if (initialStock > 0) {
          await apiFetch(`/api/v1/inventory/${product.id}/adjust`, {
            method: 'PUT',
            body: JSON.stringify({ delta: initialStock }),
          });
        }
        form.reset();
      }
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

// ---------- Pedidos ----------

const ORDER_STATUS_LABELS = { pending: 'Pendiente', paid: 'Pagado' };

async function loadOrders() {
  if (!canSeeTab('pedidos')) return;
  const tbody = document.getElementById('order-table-body');
  tbody.innerHTML = '<tr><td colspan="8">Cargando...</td></tr>';
  const status = document.getElementById('order-status-filter')?.value || '';
  try {
    const qs = status ? `&status=${encodeURIComponent(status)}` : '';
    const orders = await apiFetch(`/api/v1/orders/admin?limit=500${qs}`);
    if (orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8">No hay pedidos todavía.</td></tr>';
      return;
    }
    tbody.innerHTML = orders
      .map(
        (o) => `
        <tr>
          <td>#${o.id}</td>
          <td>${o.user_email || '-'}</td>
          <td>${ORDER_STATUS_LABELS[o.status] || o.status}</td>
          <td>$${Number(o.subtotal_amount).toLocaleString('es-CO')}</td>
          <td>$${Number(o.discount_amount).toLocaleString('es-CO')}</td>
          <td>$${Number(o.total_amount).toLocaleString('es-CO')}</td>
          <td>${new Date(o.created_at).toLocaleDateString('es-CO')}</td>
          <td>${o.items.map((i) => `${i.quantity}× ${i.product_name}`).join(', ')}</td>
        </tr>`
      )
      .join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="error">${err.message}</td></tr>`;
  }
}

function setupOrderFilter() {
  if (!canSeeTab('pedidos')) return;
  document.getElementById('order-status-filter')?.addEventListener('change', loadOrders);
}

// ---------- Exportar reportes CSV ----------

function setupCsvExportButtons() {
  const buttons = [
    { id: 'export-orders-csv', path: () => {
        const status = document.getElementById('order-status-filter')?.value || '';
        const qs = status ? `?status=${encodeURIComponent(status)}` : '';
        return `/api/v1/admin/reports/orders.csv${qs}`;
      }, filename: 'pedidos.csv' },
    { id: 'export-surveys-csv', path: () => '/api/v1/admin/reports/surveys.csv', filename: 'encuestas.csv' },
    { id: 'export-inventory-csv', path: () => '/api/v1/admin/reports/inventory.csv', filename: 'inventario.csv' },
  ];
  buttons.forEach(({ id, path, filename }) => {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener('click', async () => {
      const originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Descargando...';
      try {
        await downloadFile(path(), filename);
      } catch (err) {
        alert(`No se pudo exportar: ${err.message}`);
      } finally {
        btn.disabled = false;
        btn.textContent = originalText;
      }
    });
  });
}

// ---------- Encuestas ----------

function renderSatisfactionDistribution(distribucion) {
  if (!distribucion) return '';
  const total = Object.values(distribucion).reduce((sum, n) => sum + n, 0);
  if (total === 0) return '';
  const rows = [5, 4, 3, 2, 1]
    .map((estrella) => {
      const cantidad = distribucion[String(estrella)] || 0;
      const pct = total ? Math.round((cantidad / total) * 100) : 0;
      return `
        <div class="dist-row">
          <span class="dist-label">${'★'.repeat(estrella)}</span>
          <div class="dist-bar-track"><div class="dist-bar-fill" style="width:${pct}%"></div></div>
          <span class="dist-count">${cantidad}</span>
        </div>`;
    })
    .join('');
  return `<h3>Distribución de satisfacción general</h3><div class="dist-chart">${rows}</div>`;
}

async function loadSurveys() {
  if (!canSeeTab('encuestas')) return;
  const statsBox = document.getElementById('survey-stats');
  const distBox = document.getElementById('survey-distribution');
  const tbody = document.getElementById('survey-table-body');
  statsBox.innerHTML = 'Cargando...';
  tbody.innerHTML = '<tr><td colspan="13">Cargando...</td></tr>';
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
      renderStatTile('Calidad producto', stats.promedio_calidad_productos),
      renderStatTile('Atención recibida', stats.promedio_atencion_recibida),
      renderStatTile('Proceso de compra', stats.promedio_facilidad_proceso_compra),
      renderStatTile('Tiempo de entrega', stats.promedio_tiempo_entrega),
    ].join('');
    if (distBox) distBox.innerHTML = renderSatisfactionDistribution(stats.distribucion_nivel_satisfaccion);

    const surveys = await apiFetch('/api/v1/surveys?limit=200');
    if (surveys.length === 0) {
      tbody.innerHTML = '<tr><td colspan="13">Aún no hay respuestas.</td></tr>';
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
          <td>${s.calidad_productos ?? '-'}</td>
          <td>${s.atencion_recibida ?? '-'}</td>
          <td>${s.facilidad_proceso_compra ?? '-'}</td>
          <td>${s.tiempo_entrega ?? '-'}</td>
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
  setupOrderFilter();
  setupCsvExportButtons();
  loadDashboard();
  loadProducts();
  loadUsers();
  loadOrders();
  loadSurveys();
  loadAuditLog();
});
