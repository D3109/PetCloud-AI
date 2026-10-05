document.addEventListener('DOMContentLoaded', () => {
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('reg-email').value;
      const password = document.getElementById('reg-password').value;
      const fullName = document.getElementById('reg-fullname').value;
      const errorBox = document.getElementById('reg-error');
      errorBox.textContent = '';
      try {
        await apiFetch('/api/v1/users', {
          method: 'POST',
          body: JSON.stringify({ email, password, full_name: fullName || null }),
        });
        window.location.href = 'login.html';
      } catch (err) {
        errorBox.textContent = err.message;
      }
    });
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;
      const errorBox = document.getElementById('login-error');
      errorBox.textContent = '';
      try {
        const data = await apiFetch('/api/v1/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
        saveToken(data.access_token);
        window.location.href = 'index.html';
      } catch (err) {
        errorBox.textContent = err.message;
      }
    });
  }
});
