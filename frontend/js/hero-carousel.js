// Carrusel automatico del hero: arranca con la ilustracion de
// perro/gato (ya en el HTML como primera diapositiva) y le agrega
// fotos reales del catalogo como diapositivas siguientes. Avanza solo,
// sin botones ni controles ("solitas"), con un crossfade suave.
const HERO_SLIDE_MS = 4200;

function buildHeroSlide(product) {
  const slide = document.createElement('div');
  slide.className = 'hero-slide';
  slide.innerHTML = `
    <img src="${product.image_url}" alt="${product.name}" loading="lazy" />
    <span class="hero-slide-caption">${product.name}</span>
  `;
  return slide;
}

function startHeroCarousel(track) {
  let slides = Array.from(track.querySelectorAll('.hero-slide'));
  if (slides.length < 2) return;
  let current = 0;
  setInterval(() => {
    slides[current].classList.remove('active');
    current = (current + 1) % slides.length;
    slides[current].classList.add('active');
  }, HERO_SLIDE_MS);
}

async function initHeroCarousel() {
  const track = document.getElementById('hero-carousel');
  if (!track) return;

  try {
    const products = await apiFetch('/api/v1/products');
    // Variedad: un producto por categoria distinta, hasta 4, para no
    // repetir siempre el mismo tipo de producto en el carrusel.
    const seenCategories = new Set();
    const picks = [];
    for (const p of products) {
      if (!p.image_url) continue;
      const catKey = p.categories?.[0]?.name || 'otro';
      if (seenCategories.has(catKey)) continue;
      seenCategories.add(catKey);
      picks.push(p);
      if (picks.length >= 4) break;
    }
    picks.forEach((p) => track.appendChild(buildHeroSlide(p)));
  } catch (err) {
    // Sin catalogo disponible: se queda solo con la ilustracion, sin romper nada.
  }

  startHeroCarousel(track);
}

document.addEventListener('DOMContentLoaded', initHeroCarousel);
