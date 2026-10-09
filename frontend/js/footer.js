function renderFooter() {
  const mount = document.getElementById('site-footer');
  if (!mount) return;

  const year = new Date().getFullYear();
  mount.innerHTML = `
    <div class="site-footer-inner">
      <div>
        <p class="site-footer-brand">🐾 PetCloud</p>
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
      <p class="site-footer-bottom-made">Hecho con 🐾 para mascotas</p>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', renderFooter);
