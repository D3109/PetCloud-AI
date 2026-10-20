// Pagina tecnica standalone de auditoria (ver audit.html): logica propia,
// separada de admin.js, porque esta pagina no comparte nav/footer/tabs
// con el resto del sitio.

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value ?? '';
  return div.innerHTML;
}

function renderRows(entries) {
  return entries
    .map(
      (a) => `
      <tr>
        <td>${new Date(a.created_at).toLocaleString('es-CO')}</td>
        <td>${escapeHtml(a.actor_email || 'sistema')}</td>
        <td>${escapeHtml(a.action)}</td>
        <td>${escapeHtml(a.entity_type)}</td>
        <td>${a.entity_id ?? '-'}</td>
        <td>${escapeHtml(a.detail || '-')}</td>
      </tr>`
    )
    .join('');
}

async function loadAudit() {
  const state = document.getElementById('audit-state');
  const table = document.getElementById('audit-table');
  const body = document.getElementById('audit-table-body');
  const count = document.getElementById('audit-count');
  const limit = document.getElementById('audit-limit').value;

  table.hidden = true;
  state.hidden = false;
  state.className = 'state';
  state.textContent = 'cargando…';

  try {
    const entries = await apiFetch(`/api/v1/audit?limit=${limit}`);
    if (entries.length === 0) {
      state.textContent = 'sin actividad registrada todavía.';
      count.textContent = '';
      return;
    }
    body.innerHTML = renderRows(entries);
    count.textContent = `${entries.length} registro${entries.length === 1 ? '' : 's'}`;
    state.hidden = true;
    table.hidden = false;
  } catch (err) {
    state.className = 'state err';
    state.textContent = `error: ${err.message}`;
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }
  try {
    const me = await apiFetch('/api/v1/auth/me');
    if (!['root', 'admin'].includes(me.role)) {
      const state = document.getElementById('audit-state');
      state.className = 'state err';
      state.textContent = 'no tienes permisos para ver la auditoría.';
      return;
    }
  } catch (err) {
    window.location.href = 'login.html';
    return;
  }

  document.getElementById('audit-refresh').addEventListener('click', loadAudit);
  document.getElementById('audit-limit').addEventListener('change', loadAudit);
  loadAudit();
});
