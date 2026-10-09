const SURVEY_FIELDS = [
  'precision_recomendacion',
  'facilidad_uso',
  'confianza_usuario',
  'nivel_satisfaccion',
  'percepcion_seguridad',
  'intencion_recompra',
];

function renderLikertScale(container) {
  const field = container.dataset.field;
  container.innerHTML = [1, 2, 3, 4, 5]
    .map(
      (n) => `
      <label class="likert-option">
        <input type="radio" name="${field}" value="${n}" ${n === 3 ? 'checked' : ''} />
        <span>${n}</span>
      </label>`
    )
    .join('');
}

function getSelectedValue(field) {
  const checked = document.querySelector(`input[name="${field}"]:checked`);
  return checked ? Number(checked.value) : null;
}

document.addEventListener('DOMContentLoaded', () => {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }

  document.querySelectorAll('.likert-scale').forEach(renderLikertScale);

  const form = document.getElementById('survey-form');
  const errorBox = document.getElementById('survey-error');
  const successBox = document.getElementById('survey-success');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBox.textContent = '';
    successBox.textContent = '';

    const payload = {};
    for (const field of SURVEY_FIELDS) {
      payload[field] = getSelectedValue(field);
    }
    const comentario = document.getElementById('comentario').value.trim();
    if (comentario) payload.comentario = comentario;

    try {
      await apiFetch('/api/v1/surveys', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      successBox.textContent = '¡Gracias por tu respuesta!';
      form.reset();
      document.querySelectorAll('.likert-scale').forEach(renderLikertScale);
    } catch (err) {
      errorBox.textContent = err.message;
    }
  });
});
