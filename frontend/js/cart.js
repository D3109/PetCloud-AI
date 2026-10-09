async function loadCart() {
  const container = document.getElementById('cart-container');
  if (!isLoggedIn()) {
    container.innerHTML = '<p>Debes <a href="login.html">iniciar sesión</a> para ver tu carrito.</p>';
    return;
  }
  try {
    const cart = await apiFetch('/api/v1/cart');
    if (cart.items.length === 0) {
      container.innerHTML = '<p>Tu carrito está vacío.</p>';
      return;
    }
    container.innerHTML = `
      <table class="cart-table">
        <thead><tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Subtotal</th><th></th></tr></thead>
        <tbody>
          ${cart.items.map((item) => `
            <tr>
              <td>${item.product_name}</td>
              <td>$${Number(item.unit_price).toLocaleString('es-CO')}</td>
              <td>${item.quantity}</td>
              <td>$${Number(item.subtotal).toLocaleString('es-CO')}</td>
              <td><button class="remove-item" data-product-id="${item.product_id}">Quitar</button></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      <p class="total">Total: $${Number(cart.total).toLocaleString('es-CO')}</p>
      <button id="checkout-btn">Finalizar compra</button>
      <p id="checkout-error" class="error"></p>
    `;

    document.querySelectorAll('.remove-item').forEach((btn) => {
      btn.addEventListener('click', () => removeItem(btn.dataset.productId));
    });
    document.getElementById('checkout-btn').addEventListener('click', checkout);
  } catch (err) {
    container.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function removeItem(productId) {
  try {
    await apiFetch(`/api/v1/cart/items/${productId}`, { method: 'DELETE' });
    loadCart();
  } catch (err) {
    alert(err.message);
  }
}

async function checkout() {
  const errorBox = document.getElementById('checkout-error');
  errorBox.textContent = '';
  try {
    const order = await apiFetch('/api/v1/orders/checkout', { method: 'POST' });
    const container = document.getElementById('cart-container');
    container.innerHTML = `
      <p class="success">
        ¡Pedido #${order.id} creado! Total: $${Number(order.total_amount).toLocaleString('es-CO')}
      </p>
      <p>Ahora puedes completar el pago desde <a href="orders.html">Mis pedidos</a>.</p>
      <a href="orders.html" class="survey-cta">Ir a Mis pedidos →</a>
    `;
  } catch (err) {
    errorBox.textContent = err.message;
  }
}

document.addEventListener('DOMContentLoaded', loadCart);
