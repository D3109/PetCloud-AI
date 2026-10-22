function renderFooter() {
  const mount = document.getElementById('site-footer');
  if (!mount) return;

  const year = new Date().getFullYear();
  mount.innerHTML = `
    <div class="site-footer-inner">
      <div>
        <p class="site-footer-brand">
          <svg class="footer-paw" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5.2c-3 0-4.6 2.3-4.6 4.6 0 1 .35 1.75.9 2.45-1.5.55-2.9 1.7-2.9 3.55 0 2.1 1.9 3.2 3.9 3.2 1 0 1.85-.3 2.7-.65.85.35 1.7.65 2.7.65 2 0 3.9-1.1 3.9-3.2 0-1.85-1.4-3-2.9-3.55.55-.7.9-1.45.9-2.45 0-2.3-1.6-4.6-4.6-4.6z" fill="currentColor"/><circle cx="8.6" cy="4.4" r="1.6" fill="currentColor"/><circle cx="15.4" cy="4.4" r="1.6" fill="currentColor"/><circle cx="5.3" cy="8.6" r="1.6" fill="currentColor"/><circle cx="18.7" cy="8.6" r="1.6" fill="currentColor"/></svg>
          PetCloud
        </p>
        <p>Tienda virtual de productos para perros y gatos, con recomendaciones asistidas por IA
        para ayudarte a encontrar lo que tu mascota necesita.</p>
      </div>
      <div>
        <h3>PetCloud S.A.S.</h3>
        <p>NIT 900.000.000-1<br />Bogotá, Colombia</p>
        <p>contacto@petcloud.com</p>
      </div>
      <div>
        <h3>Enlaces</h3>
        <ul class="site-footer-links">
          <li><a href="index.html">Catálogo</a></li>
          <li><a href="survey.html">Encuesta de satisfacción</a></li>
          <li><a href="login.html">Ingresar</a></li>
        </ul>
      </div>
    </div>
    <div class="site-footer-bottom">
      <p class="site-footer-bottom-legal">
        © ${year} PetCloud. Todos los derechos reservados.
        Las ilustraciones de producto son gráficos de referencia y los nombres de marcas mencionados en el
        catálogo son propiedad de sus respectivos dueños, mostrados únicamente a modo de referencia,
        sin afiliación ni respaldo real de esas marcas.
      </p>
      <p class="site-footer-bottom-made">Hecho con <svg class="footer-paw footer-paw-inline" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5.2c-3 0-4.6 2.3-4.6 4.6 0 1 .35 1.75.9 2.45-1.5.55-2.9 1.7-2.9 3.55 0 2.1 1.9 3.2 3.9 3.2 1 0 1.85-.3 2.7-.65.85.35 1.7.65 2.7.65 2 0 3.9-1.1 3.9-3.2 0-1.85-1.4-3-2.9-3.55.55-.7.9-1.45.9-2.45 0-2.3-1.6-4.6-4.6-4.6z" fill="currentColor"/><circle cx="8.6" cy="4.4" r="1.6" fill="currentColor"/><circle cx="15.4" cy="4.4" r="1.6" fill="currentColor"/><circle cx="5.3" cy="8.6" r="1.6" fill="currentColor"/><circle cx="18.7" cy="8.6" r="1.6" fill="currentColor"/></svg> para mascotas</p>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', renderFooter);
