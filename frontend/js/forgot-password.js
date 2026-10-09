document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('forgot-form');
  const errorEl = document.getElementById('forgot-error');
  const successEl = document.getElementById('forgot-success');

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.textContent = '';
    successEl.textContent = '';
    const email = document.getElementById('forgot-email').value.trim();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const res = await apiFetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
      successEl.textContent = res.message;
      form.reset();
    } catch (err) {
      errorEl.textContent = err.message;
    } finally {
      btn.disabled = false;
    }
  });
});
