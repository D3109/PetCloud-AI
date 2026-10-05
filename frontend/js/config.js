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
