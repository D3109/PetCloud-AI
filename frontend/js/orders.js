function renderOrderCard(order) {
  const isPending = order.status === 'pending';
  const isPaid = order.status === 'paid';
  return `
    <div class="card" data-order-id="${order.id}">
      <h3>Pedido #${order.id} — <span class="order-status order-status-${order.status}">${order.status}</span></h3>
      <p class="muted">${new Date(order.created_at).toLocaleString('es-CO')}</p>
      <ul>
        ${order.items.map((item) => `<li>${item.quantity} × ${item.product_name} ($${Number(item.unit_price).toLocaleString('es-CO')})</li>`).join('')}
      </ul>
      <p class="total">Total: $${Number(order.total_amount).toLocaleString('es-CO')}</p>
      ${isPending ? `
        <button class="pay-btn" data-order-id="${order.id}">Pagar ahora</button>
        <p class="error pay-error" data-order-id="${order.id}"></p>
      ` : ''}
      ${isPaid ? `
        <p class="success">✓ Pedido pagado</p>
        <a href="survey.html?order_id=${order.id}" class="link-btn survey-cta">Contarnos tu experiencia →</a>
      ` : ''}
    </div>
  `;
}

async function loadOrders() {
  const container = document.getElementById('orders-container');
  if (!isLoggedIn()) {
    container.innerHTML = '<p>Debes <a href="login.html">iniciar sesión</a> para ver tus pedidos.</p>';
    return;
  }
  try {
    const orders = await apiFetch('/api/v1/orders');
    if (orders.length === 0) {
      container.innerHTML = '<p>Aún no tienes pedidos.</p>';
      return;
    }
    container.innerHTML = orders.map(renderOrderCard).join('');

    document.querySelectorAll('.pay-btn').forEach((btn) => {
      btn.addEventListener('click', () => payOrder(btn.dataset.orderId));
    });
  } catch (err) {
    container.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function payOrder(orderId) {
  const errorBox = document.querySelector(`.pay-error[data-order-id="${orderId}"]`);
  if (errorBox) errorBox.textContent = '';
  try {
    await apiFetch(`/api/v1/payments/${orderId}`, {
      method: 'POST',
      body: JSON.stringify({ method: 'simulated' }),
    });
    loadOrders();
  } catch (err) {
    if (errorBox) errorBox.textContent = err.message;
  }
}

document.addEventListener('DOMContentLoaded', loadOrders);
