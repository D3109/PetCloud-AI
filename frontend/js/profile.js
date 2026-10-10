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

  const petsListBox = document.getElementById('pets-list');
  const petForm = document.getElementById('pet-form');
  const speciesLabels = { perro: 'Perro', gato: 'Gato', otro: 'Otro' };

  function renderPets(pets) {
    if (!petsListBox) return;
    if (pets.length === 0) {
      petsListBox.innerHTML = '<p class="muted">Aún no has agregado ninguna mascota.</p>';
      return;
    }
    petsListBox.innerHTML = pets.map((pet) => `
      <div class="pet-card">
        <p class="pet-card-name">🐾 ${pet.name} <span class="muted">(${speciesLabels[pet.species] || pet.species})</span></p>
        ${pet.breed ? `<p class="muted">Raza: ${pet.breed}</p>` : ''}
        ${pet.birth_date ? `<p class="muted">Nació: ${pet.birth_date}</p>` : ''}
      </div>
    `).join('');
  }

  async function loadPets() {
    try {
      const pets = await apiFetch('/api/v1/pets');
      renderPets(pets);
    } catch (err) {
      if (petsListBox) petsListBox.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  if (petsListBox) {
    loadPets();
  }

  if (petForm) {
    petForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById('pet-error');
      errorBox.textContent = '';
      const name = document.getElementById('new-pet-name').value.trim();
      const species = document.getElementById('new-pet-species').value;
      const breed = document.getElementById('new-pet-breed').value.trim();
      const birthDate = document.getElementById('new-pet-birth-date').value;
      if (!name) {
        errorBox.textContent = 'Escribe el nombre de la mascota.';
        return;
      }
      try {
        await apiFetch('/api/v1/pets', {
          method: 'POST',
          body: JSON.stringify({
            name,
            species,
            breed: breed || null,
            birth_date: birthDate || null,
          }),
        });
        petForm.reset();
        loadPets();
      } catch (err) {
        errorBox.textContent = err.message;
      }
    });
  }

  const myIncidentsBox = document.getElementById('my-incidents-list');
  const incidentForm = document.getElementById('incident-form');
  const incidentStatusLabels = { abierto: 'Abierto', en_progreso: 'En progreso', resuelto: 'Resuelto', cerrado: 'Cerrado' };

  function renderMyIncidents(incidents) {
    if (!myIncidentsBox) return;
    if (incidents.length === 0) {
      myIncidentsBox.innerHTML = '<p class="muted">No has reportado ningún problema.</p>';
      return;
    }
    myIncidentsBox.innerHTML = incidents
      .map(
        (i) => `
      <div class="pet-card">
        <p class="pet-card-name">${i.title} <span class="muted">(${incidentStatusLabels[i.status] || i.status})</span></p>
        <p class="muted">${i.description}</p>
        ${i.resolution_notes ? `<p class="muted">Respuesta: ${i.resolution_notes}</p>` : ''}
      </div>
    `
      )
      .join('');
  }

  async function loadMyIncidents() {
    try {
      const incidents = await apiFetch('/api/v1/incidents/mine');
      renderMyIncidents(incidents);
    } catch (err) {
      if (myIncidentsBox) myIncidentsBox.innerHTML = `<p class="error">${err.message}</p>`;
    }
  }

  if (myIncidentsBox) {
    loadMyIncidents();
  }

  if (incidentForm) {
    incidentForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById('incident-error');
      errorBox.textContent = '';
      const title = document.getElementById('new-incident-title').value.trim();
      const description = document.getElementById('new-incident-description').value.trim();
      const priority = document.getElementById('new-incident-priority').value;
      if (!title || !description) {
        errorBox.textContent = 'Escribe un título y cuéntanos qué pasó.';
        return;
      }
      try {
        await apiFetch('/api/v1/incidents', {
          method: 'POST',
          body: JSON.stringify({ title, description, priority }),
        });
        incidentForm.reset();
        document.getElementById('new-incident-priority').value = 'media';
        loadMyIncidents();
      } catch (err) {
        errorBox.textContent = err.message;
      }
    });
  }

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
