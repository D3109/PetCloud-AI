// Widget flotante de asistente IA (PetCloud).
// Requiere config.js (API_BASE) y api.js (apiFetch, isLoggedIn) ya cargados.

document.addEventListener('DOMContentLoaded', () => {
  if (!isLoggedIn()) return; // el asistente solo aplica a usuarios autenticados

  const toggleBtn = document.createElement('button');
  toggleBtn.id = 'chat-toggle';
  toggleBtn.setAttribute('aria-label', 'Abrir asistente PetCloud con IA');
  toggleBtn.innerHTML = `
    <span id="chat-toggle-ring"></span>
    <span id="chat-toggle-icon">🐾</span>
    <span id="chat-toggle-badge">IA</span>
  `;

  const panel = document.createElement('div');
  panel.id = 'chat-panel';
  panel.className = 'hidden';
  panel.innerHTML = `
    <div id="chat-header">
      <span>Asistente PetCloud</span>
      <button id="chat-close" aria-label="Cerrar asistente">&times;</button>
    </div>
    <div id="chat-messages"></div>
    <form id="chat-form">
      <input id="chat-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" />
      <button type="submit">Enviar</button>
    </form>
  `;

  document.body.appendChild(panel);
  document.body.appendChild(toggleBtn);

  const messagesBox = panel.querySelector('#chat-messages');
  const form = panel.querySelector('#chat-form');
  const input = panel.querySelector('#chat-input');
  const closeBtn = panel.querySelector('#chat-close');

  function addMessage(text, who) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-${who}`;
    bubble.textContent = text;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function openPanel() {
    panel.classList.remove('hidden');
    if (!messagesBox.dataset.greeted) {
      addMessage('¡Hola! Soy el asistente de PetCloud. ¿En qué te ayudo hoy?', 'bot');
      messagesBox.dataset.greeted = '1';
    }
    input.focus();
  }

  function closePanel() {
    panel.classList.add('hidden');
  }

  toggleBtn.addEventListener('click', () => {
    panel.classList.contains('hidden') ? openPanel() : closePanel();
  });
  closeBtn.addEventListener('click', closePanel);

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
