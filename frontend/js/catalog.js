let ALL_PRODUCTS = [];

async function loadProducts() {
  const grid = document.getElementById('product-grid');
  grid.innerHTML = renderSkeletons();
  try {
    const [products, categories] = await Promise.all([
      apiFetch('/api/v1/products'),
      apiFetch('/api/v1/categories').catch(() => []),
    ]);
    ALL_PRODUCTS = products;
    populateCategoryFilter(categories);
    renderGrid();
  } catch (err) {
    grid.innerHTML = `<p class="error">No se pudo cargar el catálogo: ${err.message}</p>`;
  }
}

function renderSkeletons() {
  return Array.from({ length: 8 })
    .map(() => '<div class="card card-skeleton"><div class="skeleton-image"></div><div class="skeleton-line"></div><div class="skeleton-line short"></div></div>')
    .join('');
}

function populateCategoryFilter(categories) {
  const select = document.getElementById('filter-category');
  if (!select || select.dataset.populated) return;
  categories
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((c) => {
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = c.name;
      select.appendChild(opt);
    });
  select.dataset.populated = 'true';
}

function getFilters() {
  return {
    category: document.getElementById('filter-category')?.value || '',
    petType: document.getElementById('filter-pet-type')?.value || '',
    search: (document.getElementById('filter-search')?.value || '').trim().toLowerCase(),
  };
}

function renderGrid() {
  const grid = document.getElementById('product-grid');
  const { category, petType, search } = getFilters();

  const filtered = ALL_PRODUCTS.filter((p) => {
    if (category && !p.categories.some((c) => c.name === category)) return false;
    if (petType && p.pet_type !== petType) return false;
    if (search && !p.name.toLowerCase().includes(search)) return false;
    return true;
  });

  if (ALL_PRODUCTS.length === 0) {
    grid.innerHTML = '<p class="empty-state">Aún no hay productos en el catálogo.</p>';
    return;
  }
  if (filtered.length === 0) {
    grid.innerHTML = '<p class="empty-state">Ningún producto coincide con ese filtro. Prueba con otra búsqueda.</p>';
    return;
  }

  grid.innerHTML = filtered.map(renderProductCard).join('');
  grid.querySelectorAll('.add-to-cart').forEach((btn) => {
    btn.addEventListener('click', () => addToCart(btn.dataset.productId, btn));
  });
}

const PET_TYPE_LABELS = { perro: 'Perro', gato: 'Gato', ambas: 'Perro y gato', otro: 'Otro' };

function renderProductCard(product) {
  const categories = product.categories.map((c) => c.name).join(', ') || 'Sin categoría';
  const fallback =
    'https://plus.unsplash.com/premium_photo-1729111978398-821b4930c4c2?w=300&h=200&fit=crop&auto=format&q=60';
  const imgSrc = product.image_url || fallback;
  const petBadge = product.pet_type
    ? `<span class="pet-badge">${PET_TYPE_LABELS[product.pet_type] || product.pet_type}</span>`
    : '';
  return `
    <div class="card">
      <img
        class="card-image"
        src="${imgSrc}"
        alt="${product.name}"
        loading="lazy"
        onerror="this.onerror=null;this.src='${fallback}';"
      />
      <div class="card-tags">
        ${product.brand ? `<span class="muted">${product.brand}</span>` : ''}
        ${petBadge}
      </div>
      <h3>${product.name}</h3>
      <p class="muted">${categories}</p>
      <p class="price">$${Number(product.price).toLocaleString('es-CO')}</p>
      <button class="add-to-cart" data-product-id="${product.id}">Agregar al carrito</button>
    </div>
  `;
}

async function addToCart(productId, btn) {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Agregando...';
  try {
    await apiFetch('/api/v1/cart/items', {
      method: 'POST',
      body: JSON.stringify({ product_id: Number(productId), quantity: 1 }),
    });
    btn.textContent = '¡Agregado!';
    setTimeout(() => {
      btn.textContent = originalText;
      btn.disabled = false;
    }, 1200);
  } catch (err) {
    alert(err.message);
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
  ['filter-category', 'filter-pet-type'].forEach((id) => {
    document.getElementById(id)?.addEventListener('change', renderGrid);
  });
  document.getElementById('filter-search')?.addEventListener('input', renderGrid);
});
