async function loadProducts() {
  const grid = document.getElementById('product-grid');
  grid.innerHTML = '<p>Cargando productos...</p>';
  try {
    const products = await apiFetch('/api/v1/products');
    if (products.length === 0) {
      grid.innerHTML = '<p>Aún no hay productos en el catálogo.</p>';
      return;
    }
    grid.innerHTML = products.map(renderProductCard).join('');
    document.querySelectorAll('.add-to-cart').forEach((btn) => {
      btn.addEventListener('click', () => addToCart(btn.dataset.productId));
    });
  } catch (err) {
    grid.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

function renderProductCard(product) {
  const categories = product.categories.map((c) => c.name).join(', ') || 'Sin categoría';
  const fallback =
    'https://plus.unsplash.com/premium_photo-1729111978398-821b4930c4c2?w=300&h=200&fit=crop&auto=format&q=60';
  const imgSrc = product.image_url || fallback;
  return `
    <div class="card">
      <img
        class="card-image"
        src="${imgSrc}"
        alt="${product.name}"
        loading="lazy"
        onerror="this.onerror=null;this.src='${fallback}';"
      />
      <h3>${product.name}</h3>
      <p class="muted">${categories}</p>
      <p class="price">$${Number(product.price).toLocaleString('es-CO')}</p>
      <button class="add-to-cart" data-product-id="${product.id}">Agregar al carrito</button>
    </div>
  `;
}

async function addToCart(productId) {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }
  try {
    await apiFetch('/api/v1/cart/items', {
      method: 'POST',
      body: JSON.stringify({ product_id: Number(productId), quantity: 1 }),
    });
    alert('Producto agregado al carrito');
  } catch (err) {
    alert(err.message);
  }
}

document.addEventListener('DOMContentLoaded', loadProducts);
