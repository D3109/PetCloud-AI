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
    priceMin: document.getElementById('filter-price-min')?.value || '',
    priceMax: document.getElementById('filter-price-max')?.value || '',
  };
}

function renderGrid() {
  const grid = document.getElementById('product-grid');
  const { category, petType, search, priceMin, priceMax } = getFilters();
  const minPrice = priceMin !== '' ? Number(priceMin) : null;
  const maxPrice = priceMax !== '' ? Number(priceMax) : null;

  const filtered = ALL_PRODUCTS.filter((p) => {
    if (category && !p.categories.some((c) => c.name === category)) return false;
    if (petType && p.pet_type !== petType) return false;
    if (search) {
      const haystack = `${p.name} ${p.brand || ''} ${p.description || ''}`.toLowerCase();
      if (!haystack.includes(search)) return false;
    }
    const price = Number(p.price);
    if (minPrice !== null && price < minPrice) return false;
    if (maxPrice !== null && price > maxPrice) return false;
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
  grid.querySelectorAll('.view-details').forEach((btn) => {
    btn.addEventListener('click', () => {
      const product = ALL_PRODUCTS.find((p) => p.id === Number(btn.dataset.productId));
      if (product) openProductModal(product);
    });
  });
}

const PET_TYPE_LABELS = { perro: 'Perro', gato: 'Gato', ambas: 'Perro y gato', otro: 'Otro' };
const FALLBACK_IMAGE =
  'https://plus.unsplash.com/premium_photo-1729111978398-821b4930c4c2?w=300&h=200&fit=crop&auto=format&q=60';

function availabilityLabel(product) {
  const stock = product.stock_quantity ?? 0;
  if (stock <= 0) return { text: 'Agotado', cls: 'stock-out' };
  if (stock <= 5) return { text: `Quedan ${stock}`, cls: 'stock-low' };
  return { text: 'Disponible', cls: 'stock-ok' };
}

function renderProductCard(product) {
  const categories = product.categories.map((c) => c.name).join(', ') || 'Sin categoría';
  const imgSrc = product.image_url || FALLBACK_IMAGE;
  const petBadge = product.pet_type
    ? `<span class="pet-badge">${PET_TYPE_LABELS[product.pet_type] || product.pet_type}</span>`
    : '';
  const availability = availabilityLabel(product);
  return `
    <div class="card">
      <img
        class="card-image"
        src="${imgSrc}"
        alt="${product.name}"
        loading="lazy"
        onerror="this.onerror=null;this.src='${FALLBACK_IMAGE}';"
      />
      <div class="card-tags">
        ${product.brand ? `<span class="muted">${product.brand}</span>` : ''}
        ${petBadge}
        <span class="stock-badge ${availability.cls}">${availability.text}</span>
      </div>
      <h3>${product.name}</h3>
      <p class="muted">${categories}</p>
      <p class="card-description">${product.description || ''}</p>
      <p class="price">$${Number(product.price).toLocaleString('es-CO')}</p>
      <div class="card-actions">
        <button class="view-details" data-product-id="${product.id}">Ver detalles</button>
        <button class="add-to-cart" data-product-id="${product.id}" ${availability.cls === 'stock-out' ? 'disabled' : ''}>
          ${availability.cls === 'stock-out' ? 'Agotado' : 'Agregar al carrito'}
        </button>
      </div>
    </div>
  `;
}

function openProductModal(product) {
  const backdrop = document.getElementById('product-modal-backdrop');
  const content = document.getElementById('product-modal-content');
  if (!backdrop || !content) return;

  const categories = product.categories.map((c) => c.name).join(', ') || 'Sin categoría';
  const imgSrc = product.image_url || FALLBACK_IMAGE;
  const availability = availabilityLabel(product);

  content.innerHTML = `
    <button class="modal-close" aria-label="Cerrar">×</button>
    <img class="modal-image" src="${imgSrc}" alt="${product.name}"
      onerror="this.onerror=null;this.src='${FALLBACK_IMAGE}';" />
    <h2>${product.name}</h2>
    <p class="muted">${categories}${product.brand ? ' · ' + product.brand : ''}</p>
    <p class="stock-badge ${availability.cls}">${availability.text}</p>
    <p>${product.description || 'Sin descripción disponible.'}</p>
    <p class="price">$${Number(product.price).toLocaleString('es-CO')}</p>
    <button class="add-to-cart" data-product-id="${product.id}" ${availability.cls === 'stock-out' ? 'disabled' : ''}>
      ${availability.cls === 'stock-out' ? 'Agotado' : 'Agregar al carrito'}
    </button>
  `;
  backdrop.classList.remove('hidden');

  content.querySelector('.modal-close').addEventListener('click', closeProductModal);
  content.querySelector('.add-to-cart')?.addEventListener('click', (e) => {
    addToCart(product.id, e.target);
  });
}

function closeProductModal() {
  document.getElementById('product-modal-backdrop')?.classList.add('hidden');
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
  ['filter-search', 'filter-price-min', 'filter-price-max'].forEach((id) => {
    document.getElementById(id)?.addEventListener('input', renderGrid);
  });
  document.getElementById('filter-clear')?.addEventListener('click', () => {
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-pet-type').value = '';
    document.getElementById('filter-search').value = '';
    document.getElementById('filter-price-min').value = '';
    document.getElementById('filter-price-max').value = '';
    renderGrid();
  });

  const backdrop = document.getElementById('product-modal-backdrop');
  backdrop?.addEventListener('click', (e) => {
    if (e.target === backdrop) closeProductModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeProductModal();
  });
});
