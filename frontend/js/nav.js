async function renderNav() {
  const nav = document.getElementById('nav');
  if (!nav) return;

  const loggedIn = isLoggedIn();
  let isAdmin = false;

  if (loggedIn) {
    try {
      const me = await apiFetch('/api/v1/auth/me');
      isAdmin = me.role === 'admin';
    } catch (err) {
      // token invalido o expirado: lo tratamos como no logueado
      clearToken();
      window.location.href = 'login.html';
      return;
    }
  }

  nav.innerHTML = `
    <div class="nav-inner">
      <a href="index.html" class="brand">🐾 PetCloud</a>
      <div class="nav-links">
        <a href="index.html">Catálogo</a>
        ${loggedIn ? '<a href="cart.html">Carrito</a>' : ''}
        ${loggedIn ? '<a href="orders.html">Mis pedidos</a>' : ''}
        ${loggedIn ? '<a href="survey.html">Encuesta</a>' : ''}
        ${isAdmin ? '<a href="admin.html">Administrador</a>' : ''}
        ${loggedIn
          ? '<button id="logout-btn" class="link-btn">Cerrar sesión</button>'
          : '<a href="login.html">Ingresar</a><a href="register.html">Registrarme</a>'}
      </div>
    </div>
  `;

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      clearToken();
      window.location.href = 'login.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', renderNav);
