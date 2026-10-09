document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reset-form');
  const errorEl = document.getElementById('reset-error');
  const successEl = document.getElementById('reset-success');
  const tokenInput = document.getElementById('reset-token');

  // Si el enlace del correo trae ?token=..., se rellena automaticamente.
  const params = new URLSearchParams(window.location.search);
  const tokenFromUrl = params.get('token');
  if (tokenFromUrl) tokenInput.value = tokenFromUrl;

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.textContent = '';
    successEl.textContent = '';

    const token = tokenInput.value.trim();
    const password = document.getElementById('reset-password').value;
    const passwordConfirm = document.getElementById('reset-password-confirm').value;

    if (password !== passwordConfirm) {
      errorEl.textContent = 'Las contraseñas no coinciden.';
      return;
    }

    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const res = await apiFetch('/api/v1/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token, new_password: password }),
      });
      successEl.textContent = `${res.message} Redirigiendo...`;
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 2000);
    } catch (err) {
      errorEl.textContent = err.message;
      btn.disabled = false;
    }
  });
});
