async function renderNav() {
  const nav = document.getElementById('nav');
  if (!nav) return;

  const STAFF_ROLES = ['root', 'admin', 'gestor_productos', 'atencion_cliente'];
  const loggedIn = isLoggedIn();
  const onCatalog = /(^|\/)index\.html$/.test(window.location.pathname) || window.location.pathname.endsWith('/');

  const accountMenuItems = loggedIn
    ? `
      <a href="profile.html">Mi perfil</a>
      <a href="orders.html">Mis pedidos</a>
      <a href="survey.html">Encuesta</a>
      <button id="logout-btn" class="link-btn">Cerrar sesión</button>
    `
    : `
      <a href="login.html">Ingresar</a>
      <a href="register.html">Registrarme</a>
    `;

  // Filtros del catalogo (categoria, mascota, precio): se agregan al nav
  // SOLO en index.html, como una segunda fila pegada a la barra principal
  // -combinados con el buscador en una sola barra arriba, en vez de su
  // propia fila separada mas abajo, despues del banner-.
  const catalogFiltersHTML = onCatalog
    ? `
      <div class="filters nav-filters">
        <select id="filter-category">
          <option value="">Todas las categorías</option>
        </select>
        <select id="filter-pet-type">
          <option value="">Todas las mascotas</option>
          <option value="perro">Perro</option>
          <option value="gato">Gato</option>
          <option value="ambas">Ambas</option>
          <option value="otro">Otro</option>
        </select>
        <div class="price-filter">
          <input id="filter-price-min" type="number" min="0" step="1000" placeholder="Precio mín." />
          <span class="price-filter-sep">—</span>
          <input id="filter-price-max" type="number" min="0" step="1000" placeholder="Precio máx." />
        </div>
        <button type="button" id="filter-clear" class="btn-small">Limpiar filtros</button>
      </div>
    `
    : '';

  // Todo esto se pinta de una sola vez, SIN esperar ninguna llamada a la
  // API (el chequeo de rol/admin queda al final, en segundo plano): si el
  // nav quedara pausado esperando /auth/me antes de pintarse, catalog.js
  // (que arranca su propia carga apenas el DOM esta listo) podria terminar
  // de traer las categorias ANTES de que el <select> exista todavia, y esas
  // categorias nunca se volverian a poblar.
  nav.innerHTML = `
    <div class="nav-inner">
      <a href="index.html" class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="15.3" rx="5.8" ry="4.5" fill="currentColor"/><ellipse cx="4.9" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/><ellipse cx="8.8" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="15.2" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="19.1" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/></svg>
        </span>
        Pet Cloud IA
      </a>

      <form id="nav-search-form" class="nav-search" role="search">
        <svg class="nav-search-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/><line x1="16.3" y1="16.3" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <input id="nav-search-input" type="text" placeholder="Buscar productos..." aria-label="Buscar productos" autocomplete="off" />
        <button type="button" id="nav-search-clear" class="nav-search-clear hidden" aria-label="Limpiar búsqueda">&times;</button>
      </form>

      <div class="nav-links">
        <a href="index.html?mascota=perro">Perros</a>
        <a href="index.html?mascota=gato">Gatos</a>
        <a href="index.html#ofertas">Ofertas</a>
        <div class="nav-account">
          <button type="button" id="nav-account-btn" class="link-btn nav-account-btn">Mi cuenta</button>
          <div id="nav-account-menu" class="nav-account-menu hidden">${accountMenuItems}</div>
        </div>
      </div>

      <a href="${loggedIn ? 'cart.html' : 'login.html'}" class="nav-cart" aria-label="Ir al carrito">
        <svg viewBox="0 0 24 24" fill="none"><path d="M3 4h2l2.4 11.4a2 2 0 002 1.6h7.7a2 2 0 002-1.6L20.5 8H6.2" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="20" r="1.4" fill="#fff"/><circle cx="17" cy="20" r="1.4" fill="#fff"/></svg>
      </a>
    </div>
    ${catalogFiltersHTML}
  `;

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      clearToken();
      window.location.href = 'login.html';
    });
  }

  // Menu desplegable "Mi cuenta"
  const accountBtn = document.getElementById('nav-account-btn');
  const accountMenu = document.getElementById('nav-account-menu');
  if (accountBtn && accountMenu) {
    accountBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      accountMenu.classList.toggle('hidden');
    });
    document.addEventListener('click', (e) => {
      if (!accountMenu.contains(e.target) && e.target !== accountBtn) {
        accountMenu.classList.add('hidden');
      }
    });
  }

  // Buscador del nav: es el UNICO buscador de texto del catalogo (ya no hay
  // un segundo campo de busqueda dentro de los filtros, para no mostrar dos
  // buscadores a la vez). En el catalogo filtra en vivo llamando directo a
  // renderGrid() (definida en catalog.js); en otras paginas navega con ?q=.
  const searchForm = document.getElementById('nav-search-form');
  const searchInput = document.getElementById('nav-search-input');
  const searchClear = document.getElementById('nav-search-clear');

  if (onCatalog) {
    const q = new URLSearchParams(window.location.search).get('q');
    if (q) searchInput.value = q;
    searchClear.classList.toggle('hidden', !searchInput.value);
    searchInput.addEventListener('input', () => {
      searchClear.classList.toggle('hidden', !searchInput.value);
      if (typeof renderGrid === 'function') renderGrid();
    });
  }

  searchForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = searchInput.value.trim();
    if (onCatalog) return; // ya filtra en vivo
    window.location.href = q ? `index.html?q=${encodeURIComponent(q)}` : 'index.html';
  });

  searchClear?.addEventListener('click', () => {
    searchInput.value = '';
    searchClear.classList.add('hidden');
    if (onCatalog && typeof renderGrid === 'function') renderGrid();
    searchInput.focus();
  });

  // Chequeo de rol (staff/admin) en segundo plano: agrega el enlace
  // "Administrador" al menu si corresponde, sin bloquear el resto del nav
  // (buscador y filtros) mientras se resuelve esta llamada.
  if (loggedIn) {
    try {
      const me = await apiFetch('/api/v1/auth/me');
      const isAdmin = STAFF_ROLES.includes(me.role);
      if (isAdmin && accountMenu) {
        const adminLink = document.createElement('a');
        adminLink.href = 'admin.html';
        adminLink.textContent = 'Administrador';
        const logout = document.getElementById('logout-btn');
        if (logout) accountMenu.insertBefore(adminLink, logout);
        else accountMenu.appendChild(adminLink);
      }
    } catch (err) {
      // token invalido o expirado: lo tratamos como no logueado
      clearToken();
      window.location.href = 'login.html';
    }
  }
}

document.addEventListener('DOMContentLoaded', renderNav);
