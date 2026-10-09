function resolveApiBase() {
  const { hostname, protocol } = window.location;
  // En Codespaces, cada puerto forma su propia URL: ...-5500.app.github.dev
  // Esto la convierte en la URL del backend: ...-8000.app.github.dev
  const match = hostname.match(/^(.*)-\d+\.app\.github\.dev$/);
  if (match) {
    return `${protocol}//${match[1]}-8000.app.github.dev`;
  }
  return 'http://localhost:8000';
}

const API_BASE = resolveApiBase();

// ID de cliente OAuth de Google para el boton "Ingresar con Google".
// Se obtiene gratis en https://console.cloud.google.com/apis/credentials
// (tipo "ID de cliente de OAuth" > "Aplicacion web"). Mientras esto sea
// null, el boton de Google simplemente no se muestra (ver google-auth.js).
const GOOGLE_CLIENT_ID = null;
