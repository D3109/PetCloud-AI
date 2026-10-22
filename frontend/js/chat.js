// Widget flotante de asistente IA (PetCloud).
// Requiere config.js (API_BASE) y api.js (apiFetch, isLoggedIn) ya cargados.

document.addEventListener('DOMContentLoaded', () => {
  if (!isLoggedIn()) return; // el asistente solo aplica a usuarios autenticados

  const toggleWrap = document.createElement('div');
  toggleWrap.id = 'chat-toggle-wrap';
  toggleWrap.innerHTML = `
    <span id="chat-toggle-bubble" class="hidden">Habla con Pet-IA</span>
    <button id="chat-toggle" aria-label="Abrir asistente PetCloud con IA">
      <span id="chat-toggle-ring"></span>
      <span id="chat-toggle-icon"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><ellipse cx="12" cy="15.3" rx="5.8" ry="4.5" fill="currentColor"/><ellipse cx="4.9" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/><ellipse cx="8.8" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="15.2" cy="5.6" rx="2.3" ry="2.8" fill="currentColor"/><ellipse cx="19.1" cy="10.4" rx="2.1" ry="2.6" fill="currentColor"/></svg></span>
      <span id="chat-toggle-badge">IA</span>
    </button>
  `;
  const toggleBtn = toggleWrap.querySelector('#chat-toggle');

  const panel = document.createElement('div');
  panel.id = 'chat-panel';
  panel.className = 'hidden';
  panel.innerHTML = `
    <div id="chat-header">
      <span>Asistente PetCloud</span>
      <button id="chat-close" aria-label="Cerrar asistente">&times;</button>
    </div>
    <p id="chat-ai-warning">⚠️ Respuestas generadas por IA: pueden contener errores. Verifica la información importante.</p>
    <div id="chat-messages"></div>
    <form id="chat-form">
      <input id="chat-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" />
      <button type="submit">Enviar</button>
    </form>
  `;

  document.body.appendChild(panel);
  document.body.appendChild(toggleWrap);
  const toggleBubble = toggleWrap.querySelector('#chat-toggle-bubble');

  const messagesBox = panel.querySelector('#chat-messages');
  const form = panel.querySelector('#chat-form');
  const input = panel.querySelector('#chat-input');
  const closeBtn = panel.querySelector('#chat-close');

  // La burbuja "Habla con Pet-IA" es bastante ancha (~220px con el boton
  // redondo) y vive fija abajo a la derecha: en paginas donde algun
  // contenido tambien cae en esa esquina (p. ej. "Limpiar filtros" del
  // catalogo en ventanas de poca altura), la burbuja lo tapaba todo el
  // tiempo. Mostrandola solo unos segundos y dejando despues solo el
  // boton redondo (mucho mas angosto) baja muchisimo esa posibilidad,
  // sin perder el aviso inicial de que el chat existe.
  let bubbleTimer = null;
  function showBubbleTemporarily() {
    toggleBubble.classList.remove('hidden');
    clearTimeout(bubbleTimer);
    bubbleTimer = setTimeout(() => toggleBubble.classList.add('hidden'), 4500);
  }

  function addMessage(text, who) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-${who}`;
    bubble.textContent = text;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function openPanel() {
    panel.classList.remove('hidden');
    clearTimeout(bubbleTimer);
    toggleBubble.classList.add('hidden');
    if (!messagesBox.dataset.greeted) {
      addMessage('¡Hola! Soy el asistente de PetCloud. ¿En qué te ayudo hoy?', 'bot');
      messagesBox.dataset.greeted = '1';
    }
    input.focus();
  }

  function closePanel() {
    panel.classList.add('hidden');
    showBubbleTemporarily();
  }

  toggleBtn.addEventListener('click', () => {
    panel.classList.contains('hidden') ? openPanel() : closePanel();
  });
  closeBtn.addEventListener('click', closePanel);
  showBubbleTemporarily();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    input.disabled = true;

    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble chat-bot chat-typing';
    typingBubble.textContent = 'Escribiendo...';
    messagesBox.appendChild(typingBubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
      const data = await apiFetch('/api/v1/ai/assistant', {
        method: 'POST',
        body: JSON.stringify({ message }),
      });
      typingBubble.remove();
      addMessage(data.reply, 'bot');
    } catch (err) {
      typingBubble.remove();
      addMessage(`Error: ${err.message}`, 'bot');
    } finally {
      input.disabled = false;
      input.focus();
    }
  });
});
