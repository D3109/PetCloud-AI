function renderFooter() {
  const mount = document.getElementById('site-footer');
  if (!mount) return;

  const year = new Date().getFullYear();
  mount.innerHTML = `
    <div class="site-footer-inner">
      <div>
        <p class="site-footer-brand">
          <svg class="footer-paw" viewBox="0 0 24 24" fill="none" aria-hidden="true"><ellipse cx="12" cy="15.3" rx="5.8" ry="4.5" fill="currentColor"/><ellipse cx="4.9" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/><ellipse cx="8.8" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="15.2" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="19.1" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/></svg>
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
      <p class="site-footer-bottom-made">Hecho con <svg class="footer-paw footer-paw-inline" viewBox="0 0 24 24" fill="none" aria-hidden="true"><ellipse cx="12" cy="15.3" rx="5.8" ry="4.5" fill="currentColor"/><ellipse cx="4.9" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/><ellipse cx="8.8" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="15.2" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="19.1" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/></svg> para mascotas</p>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', renderFooter);
