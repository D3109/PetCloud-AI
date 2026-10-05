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
    container.innerHTML = orders.map((order) => `
      <div class="card">
        <h3>Pedido #${order.id} — ${order.status}</h3>
        <p class="muted">${new Date(order.created_at).toLocaleString('es-CO')}</p>
        <ul>
          ${order.items.map((item) => `<li>${item.quantity} × ${item.product_name} ($${Number(item.unit_price).toLocaleString('es-CO')})</li>`).join('')}
        </ul>
        <p class="total">Total: $${Number(order.total_amount).toLocaleString('es-CO')}</p>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', loadOrders);
