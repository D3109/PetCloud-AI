const TOKEN_KEY = 'petcloud_token';

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
function isLoggedIn() {
  return !!getToken();
}

async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = (data && data.detail) || `Error ${response.status}`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return data;
}

// Descarga un archivo (CSV u otro) que requiere el token de autorizacion.
// No se puede usar un <a href> normal porque el navegador no enviaria el
// header Authorization, asi que se pide con fetch, se arma un blob y se
// dispara la descarga con un enlace temporal.
async function downloadFile(path, filename) {
  const token = getToken();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const message = (data && data.detail) || `Error ${response.status}`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
