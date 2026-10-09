document.addEventListener('DOMContentLoaded', () => {
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    const addPetCheckbox = document.getElementById('reg-add-pet');
    const petFields = document.getElementById('reg-pet-fields');
    if (addPetCheckbox && petFields) {
      addPetCheckbox.addEventListener('change', () => {
        petFields.hidden = !addPetCheckbox.checked;
      });
    }

    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('reg-email').value;
      const password = document.getElementById('reg-password').value;
      const passwordConfirm = document.getElementById('reg-password-confirm').value;
      const fullName = document.getElementById('reg-fullname').value;
      const phone = document.getElementById('reg-phone').value;
      const address = document.getElementById('reg-address').value;
      const errorBox = document.getElementById('reg-error');
      errorBox.textContent = '';

      if (password !== passwordConfirm) {
        errorBox.textContent = 'Las contraseñas no coinciden.';
        return;
      }

      let pet = null;
      if (addPetCheckbox && addPetCheckbox.checked) {
        const petName = document.getElementById('pet-name').value.trim();
        const petSpecies = document.getElementById('pet-species').value;
        const petBreed = document.getElementById('pet-breed').value.trim();
        const petBirthDate = document.getElementById('pet-birth-date').value;
        if (!petName) {
          errorBox.textContent = 'Escribe el nombre de tu mascota, o desmarca la casilla si no quieres añadirla ahora.';
          return;
        }
        pet = {
          name: petName,
          species: petSpecies,
          breed: petBreed || null,
          birth_date: petBirthDate || null,
        };
      }

      try {
        await apiFetch('/api/v1/users', {
          method: 'POST',
          body: JSON.stringify({
            email,
            password,
            full_name: fullName || null,
            phone: phone || null,
            address: address || null,
            pet,
          }),
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
