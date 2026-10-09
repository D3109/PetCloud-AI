// Integracion de "Ingresar con Google" (Google Identity Services).
//
// Si GOOGLE_CLIENT_ID (definido en config.js) esta vacio, no se renderiza
// nada: el resto del login/registro local sigue funcionando igual. Cuando
// se configure un Client ID real, el boton aparece automaticamente, sin
// tocar ningun otro archivo.
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('google-signin-container');
  if (!container) return;

  if (!GOOGLE_CLIENT_ID) {
    container.innerHTML =
      '<p class="muted small">Ingreso con Google no disponible todavia.</p>';
    return;
  }

  const script = document.createElement('script');
  script.src = 'https://accounts.google.com/gsi/client';
  script.async = true;
  script.defer = true;
  script.onload = () => {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleCredential,
    });
    window.google.accounts.id.renderButton(container, {
      theme: 'outline',
      size: 'large',
      text: 'continue_with',
      locale: 'es',
    });
  };
  document.head.appendChild(script);
});

async function handleGoogleCredential(response) {
  const errorBox =
    document.getElementById('login-error') || document.getElementById('reg-error');
  try {
    const data = await apiFetch('/api/v1/auth/google', {
      method: 'POST',
      body: JSON.stringify({ id_token: response.credential }),
    });
    saveToken(data.access_token);
    window.location.href = 'index.html';
  } catch (err) {
    if (errorBox) errorBox.textContent = err.message;
  }
}
