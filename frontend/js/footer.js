function renderFooter() {
  const mount = document.getElementById('site-footer');
  if (!mount) return;

  const year = new Date().getFullYear();
  mount.innerHTML = `
    <div class="site-footer-inner">
      <div>
        <p class="site-footer-brand">🐾 PetCloud</p>
        <p>Tienda virtual de productos para perros y gatos, con recomendaciones asistidas por IA.
        Proyecto de demostración con fines educativos.</p>
      </div>
      <div>
        <h3>PetCloud S.A.S. (demo)</h3>
        <p>NIT 900.000.000-1 (ficticio)<br />Bogotá, Colombia</p>
        <p>contacto@petcloud.demo</p>
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
      © ${year} PetCloud. Todos los derechos reservados. Proyecto de demostración, sin fines comerciales reales.
      Las imágenes de productos son fotografías de stock (Unsplash) usadas con fines ilustrativos;
      los nombres de marcas mencionados en el catálogo son propiedad de sus respectivos dueños y se
      muestran únicamente a modo de referencia, sin afiliación ni respaldo real de esas marcas.
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', renderFooter);
