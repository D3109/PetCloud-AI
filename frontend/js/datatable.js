// Comportamiento generico de "data table" para cualquier tabla con clase
// .admin-table o .cart-table: clic en un encabezado ordena la tabla por
// esa columna (texto o numero, detectado automaticamente), sin tener que
// tocar cada funcion de render de admin.js. Funciona incluso despues de
// que admin.js reemplace el <tbody> (las filas se vuelven a leer del DOM
// en cada clic, no se guardan en una variable).

const _sortableTablesSeen = new WeakSet();

function scanForSortableTables(root) {
  root.querySelectorAll('table.admin-table, table.cart-table').forEach((table) => {
    if (_sortableTablesSeen.has(table)) return;
    _sortableTablesSeen.add(table);
    initSortableTable(table);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  scanForSortableTables(document);

  // Algunas tablas (ej. el carrito) se inyectan por JS despues de cargar
  // la pagina, cuando llega la respuesta de la API: las detectamos con un
  // observer en vez de tener que tocar cada script que arma su tabla.
  const observer = new MutationObserver(() => scanForSortableTables(document));
  observer.observe(document.body, { childList: true, subtree: true });
});

function initSortableTable(table) {
  const headerRow = table.querySelector('thead tr');
  if (!headerRow) return;
  const ths = Array.from(headerRow.children);
  ths.forEach((th, index) => {
    const label = (th.textContent || '').trim().toLowerCase();
    if (th.classList.contains('no-sort') || label === 'acciones') return;
    th.classList.add('sortable-col');
    th.addEventListener('click', () => sortTableByColumn(table, index, th, ths));
  });
}

function isNumericLike(text) {
  return /^\$?-?[\d.,]+%?$/.test(text.trim()) && /\d/.test(text);
}

function toComparableNumber(text) {
  const cleaned = text.trim().replace(/[$%]/g, '').replace(/\./g, '').replace(',', '.');
  const n = parseFloat(cleaned);
  return Number.isNaN(n) ? null : n;
}

function sortTableByColumn(table, index, th, allThs) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  if (!rows.length) return;

  const nextDir = th.dataset.dir === 'asc' ? 'desc' : 'asc';
  allThs.forEach((h) => {
    h.dataset.dir = '';
    h.classList.remove('sorted-asc', 'sorted-desc');
  });
  th.dataset.dir = nextDir;
  th.classList.add(nextDir === 'asc' ? 'sorted-asc' : 'sorted-desc');

  const getText = (row) => {
    const cell = row.children[index];
    return cell ? cell.textContent.trim() : '';
  };

  rows.sort((a, b) => {
    const ta = getText(a);
    const tb = getText(b);
    let cmp;
    if (isNumericLike(ta) && isNumericLike(tb)) {
      cmp = toComparableNumber(ta) - toComparableNumber(tb);
    } else {
      cmp = ta.localeCompare(tb, 'es', { sensitivity: 'base', numeric: true });
    }
    return nextDir === 'asc' ? cmp : -cmp;
  });

  rows.forEach((row) => tbody.appendChild(row));
}
