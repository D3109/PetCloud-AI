document.addEventListener('DOMContentLoaded', async () => {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }

  const emailInput = document.getElementById('profile-email');
  const fullnameInput = document.getElementById('profile-fullname');
  const phoneInput = document.getElementById('profile-phone');
  const addressInput = document.getElementById('profile-address');
  const passwordSection = document.getElementById('password-section');

  try {
    const me = await apiFetch('/api/v1/auth/me');
    emailInput.value = me.email;
    fullnameInput.value = me.full_name || '';
    phoneInput.value = me.phone || '';
    addressInput.value = me.address || '';
    if (me.auth_provider === 'google' && passwordSection) {
      passwordSection.innerHTML =
        '<h2>Cambiar contraseña</h2><p class="muted">Esta cuenta inicia sesión con Google, no tiene contraseña local que cambiar aquí.</p>';
    }
  } catch (err) {
    document.getElementById('profile-error').textContent = err.message;
  }

  const profileForm = document.getElementById('profile-form');
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById('profile-error');
    const successBox = document.getElementById('profile-success');
    errorBox.textContent = '';
    successBox.textContent = '';
    try {
      await apiFetch('/api/v1/auth/me', {
        method: 'PATCH',
        body: JSON.stringify({
          full_name: fullnameInput.value || null,
          phone: phoneInput.value || null,
          address: addressInput.value || null,
        }),
      });
      successBox.textContent = 'Datos actualizados.';
    } catch (err) {
      errorBox.textContent = err.message;
    }
  });

  const passwordForm = document.getElementById('password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById('password-error');
      const successBox = document.getElementById('password-success');
      errorBox.textContent = '';
      successBox.textContent = '';
      const currentPassword = document.getElementById('current-password').value;
      const newPassword = document.getElementById('new-password').value;
      if (!currentPassword || !newPassword) {
        errorBox.textContent = 'Completa ambos campos.';
        return;
      }
      try {
        await apiFetch('/api/v1/auth/me', {
          method: 'PATCH',
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        });
        successBox.textContent = 'Contraseña actualizada.';
        passwordForm.reset();
      } catch (err) {
        errorBox.textContent = err.message;
      }
    });
  }
});
