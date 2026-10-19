// Tarjeta "Consejo del dia": consulta /api/v1/weather-tip (clima real via
// Open-Meteo, en el backend) y muestra una recomendacion corta de cuidado
// de mascotas segun el clima de hoy. Si la API externa falla, el backend
// igual responde un tip generico (available: false) que se muestra sin
// mencionar el clima, asi que la tarjeta nunca se rompe ni queda vacia.
async function loadWeatherTip() {
  const el = document.getElementById('weather-tip');
  if (!el) return;
  try {
    const data = await apiFetch('/api/v1/weather-tip');
    const climaTxt = data.available
      ? `${Math.round(data.temperature)}°C y ${data.condition} en ${data.city}`
      : 'Consejo del día';
    el.innerHTML = `
      <span class="weather-tip-icon" aria-hidden="true">🌤️</span>
      <span>
        <strong>${climaTxt}:</strong> ${data.tip}
      </span>
    `;
    el.classList.remove('hidden');
  } catch (err) {
    // Si ni el endpoint responde, se oculta la tarjeta en vez de mostrar un error.
    el.classList.add('hidden');
  }
}

document.addEventListener('DOMContentLoaded', loadWeatherTip);
