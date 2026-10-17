"""Carga categorias y productos de ejemplo para PetCloud IA.

Uso (desde backend/, con el entorno virtual / dependencias activas):
    python3 scripts/seed_products.py

Es idempotente: si una categoria ya existe no la duplica, y si un SKU ya
existe actualiza su imagen (image_url) para que corresponda al producto,
en vez de dejarla con una imagen genérica aleatoria.
No necesita token de administrador porque escribe directo a la base de
datos usando los mismos modelos de SQLAlchemy que usa la API.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.services import inventory_service

CATEGORIES = [
    ("Alimento", "Alimento seco y húmedo para perros y gatos"),
    ("Juguetes", "Juguetes para entretenimiento y ejercicio"),
    ("Higiene", "Productos de limpieza y cuidado"),
    ("Accesorios", "Correas, collares, camas y transportadoras"),
    ("Salud", "Suplementos y cuidado veterinario básico"),
    ("Medicamentos", "Medicamentos y tratamientos de venta libre para mascotas"),
]

# (nombre, sku, precio, descripcion, categoria)
PRODUCTS = [
    ("Croquetas Adulto Perro 15kg", "ALM-PER-001", "189900", "Alimento balanceado para perros adultos, todas las razas", "Alimento"),
    ("Croquetas Cachorro 7kg", "ALM-PER-002", "109900", "Fórmula de crecimiento para cachorros", "Alimento"),
    ("Alimento Húmedo Gato Salmón 85g", "ALM-GAT-001", "6900", "Lata de alimento húmedo sabor salmón", "Alimento"),
    ("Croquetas Gato Adulto 3kg", "ALM-GAT-002", "72900", "Alimento balanceado para gatos adultos", "Alimento"),
    ("Snacks Dentales Perro x10", "ALM-PER-003", "34900", "Premios que ayudan a la limpieza dental", "Alimento"),
    ("Pelota de Caucho Resistente", "JUG-001", "19900", "Pelota de caucho natural para morder y jugar", "Juguetes"),
    ("Ratón de Peluche con Sonido", "JUG-002", "12900", "Juguete para gatos con sonido de ratón", "Juguetes"),
    ("Cuerda para Jalar", "JUG-003", "15900", "Cuerda de algodón trenzada resistente a mordidas", "Juguetes"),
    ("Shampoo Hipoalergénico 500ml", "HIG-001", "28900", "Shampoo suave para pieles sensibles", "Higiene"),
    ("Toallitas Húmedas x40", "HIG-002", "17900", "Toallitas de limpieza rápida para patas y pelaje", "Higiene"),
    ("Arena Sanitaria Aglomerante 10kg", "HIG-003", "45900", "Arena para gatos con control de olores", "Higiene"),
    ("Cepillo Removedor de Pelo", "HIG-004", "22900", "Cepillo para desenredar y remover pelo muerto", "Higiene"),
    ("Correa Retráctil 5m", "ACC-001", "49900", "Correa retráctil resistente, hasta 25kg", "Accesorios"),
    ("Collar Ajustable Reflectivo", "ACC-002", "24900", "Collar con tira reflectiva para paseos nocturnos", "Accesorios"),
    ("Cama Acolchada Mediana", "ACC-003", "89900", "Cama suave y lavable, talla mediana", "Accesorios"),
    ("Transportadora Plástica S", "ACC-004", "129900", "Transportadora rígida para mascotas pequeñas", "Accesorios"),
    ("Comedero Doble Acero Inoxidable", "ACC-005", "32900", "Comedero antideslizante de dos compartimentos", "Accesorios"),
    ("Suplemento Vitamínico x60 tabletas", "SAL-001", "39900", "Complejo vitamínico para perros y gatos", "Salud"),
    ("Antipulgas Pipeta Perro Mediano", "SAL-002", "44900", "Protección mensual contra pulgas y garrapatas", "Salud"),
    ("Probiótico Digestivo x30", "SAL-003", "36900", "Apoyo a la flora intestinal de mascotas", "Salud"),
    ("Alimento Senior Perro Raza Grande 12kg", "ALM-PER-004", "169900", "Fórmula para perros mayores de razas grandes, con glucosamina", "Alimento"),
    ("Snacks Liofilizados Gato x50g", "ALM-GAT-003", "24900", "Premios liofilizados de pollo, 100% naturales", "Alimento"),
    ("Alimento Húmedo Perro Pollo y Arroz 400g", "ALM-PER-005", "8900", "Lata de alimento húmedo sabor pollo y arroz", "Alimento"),
    ("Varita con Plumas para Gato", "JUG-004", "14900", "Varita interactiva con plumas para estimular el instinto de caza", "Juguetes"),
    ("Hueso de Nylon para Masticar", "JUG-005", "17900", "Hueso resistente de nylon, ayuda a la limpieza dental", "Juguetes"),
    ("Colonia para Mascotas 100ml", "HIG-005", "19900", "Colonia suave de uso post-baño, hipoalergénica", "Higiene"),
    ("Cortaúñas para Mascotas", "HIG-006", "15900", "Cortaúñas de acero inoxidable con protector de seguridad", "Higiene"),
    ("Placa de Identificación Grabada", "ACC-006", "12900", "Placa metálica grabada con nombre y teléfono de contacto", "Accesorios"),
    ("Comedero de Viaje Plegable", "ACC-007", "18900", "Comedero/bebedero de silicona plegable para paseos y viajes", "Accesorios"),
    ("Rascador para Gato con Poste", "ACC-008", "99900", "Rascador vertical con poste de sisal y plataforma superior", "Accesorios"),
    ("Aceite de Salmón para Piel y Pelaje", "SAL-004", "42900", "Suplemento Omega 3 para piel y pelaje brillante", "Salud"),
    ("Electrolitos Rehidratantes x10 sobres", "SAL-005", "27900", "Sobres de electrolitos para apoyar la hidratación de la mascota", "Salud"),
    ("Antiparasitario Interno Perro x4 comprimidos", "MED-001", "32900", "Desparasitante interno de amplio espectro para perros", "Medicamentos"),
    ("Antiparasitario Interno Gato x4 comprimidos", "MED-002", "29900", "Desparasitante interno de amplio espectro para gatos", "Medicamentos"),
    ("Suero Oral Rehidratante Veterinario 250ml", "MED-003", "22900", "Solución rehidratante oral de uso veterinario", "Medicamentos"),
    ("Pomada Cicatrizante para Heridas 30g", "MED-004", "18900", "Pomada tópica para heridas menores, uso veterinario", "Medicamentos"),
    # Productos de marcas reconocidas, agregados a pedido del cliente. La
    # marca es solo el dato de texto "brand" (informativo, como en
    # cualquier catalogo); el icono sigue siendo una ilustracion generica
    # del tipo de producto (no un empaque oficial de esas marcas), igual
    # que el resto del catalogo.
    ("Alimento Royal Canin Adulto Raza Mediana 15kg", "BRA-001", "285000", "Alimento seco completo para perros adultos de raza mediana", "Alimento"),
    ("Alimento Hill's Science Diet Senior 7+ 12kg", "BRA-002", "320000", "Alimento seco especializado para perros senior mayores de 7 años", "Alimento"),
    ("Alimento Purina Pro Plan Gato Esterilizado 7.5kg", "BRA-003", "195000", "Alimento seco para gatos esterilizados adultos", "Alimento"),
    ("Alimento Whiskas Adulto Sabor Pollo 8kg", "BRA-004", "98000", "Alimento seco para gatos adultos sabor pollo", "Alimento"),
    ("Alimento Eukanuba Cachorro Razas Grandes 15kg", "BRA-005", "265000", "Alimento seco para cachorros de razas grandes en crecimiento", "Alimento"),
    ("Premios Pedigree Dentastix Perro Mediano x28", "BRA-006", "45000", "Snack dental masticable que ayuda a reducir el sarro", "Alimento"),
    ("Suplemento Multivitamínico VetriScience 60 tabletas", "BRA-007", "89000", "Complejo multivitamínico para apoyar la salud general de perros y gatos", "Salud"),
    ("Antiparasitario NexGard Spectra Perro x3 comprimidos", "BRA-008", "115000", "Tabletas masticables contra pulgas, garrapatas y parásitos internos", "Medicamentos"),
    ("Antiparasitario Drontal Plus Perro x2 tabletas", "BRA-009", "42000", "Tabletas desparasitantes de amplio espectro para perros", "Medicamentos"),
]

# ---------------------------------------------------------------------
# Imagenes de producto: iconos planos generados por categoria (en vez de
# 45 SVG distintos escritos a mano). Cada categoria tiene un unico icono
# con la paleta de marca actual (terracota + crema), y el fondo de la
# tarjeta rota entre unos pocos tonos suaves (segun el SKU) para que no
# se vean todas identicas dentro de una misma categoria. Esto reemplaza
# el enfoque anterior (colores que no seguian la paleta de marca y
# trazos negros tipo caricatura) por algo mas simple, coherente y facil
# de mantener: para una imagen real de producto, basta con cargar su
# propia "URL de imagen" desde el panel de administrador.
# ---------------------------------------------------------------------
import hashlib
from urllib.parse import quote

_PRIMARY = "#c1694f"
_PRIMARY_DARK = "#a1543e"
_ACCENT = "#e8935f"
_INK = "#1f4743"

_CARD_BG = ["#f6d9c2", "#f0e0cd", "#e7cdb8", "#dce9e7", "#f2ebdf"]


def _bg_for_sku(sku: str) -> str:
    idx = int(hashlib.md5(sku.encode("utf-8")).hexdigest(), 16) % len(_CARD_BG)
    return _CARD_BG[idx]


def _icon_markup(category: str) -> str:
    """Icono plano (sin degradados ni contornos negros) para la categoria dada."""
    if category == "Alimento":
        return (
            f"<ellipse cx='200' cy='148' rx='96' ry='24' fill='{_ACCENT}'/>"
            f"<path d='M104,148 Q104,262 200,262 Q296,262 296,148 L272,148 "
            f"Q272,234 200,234 Q128,234 128,148 Z' fill='{_PRIMARY}'/>"
            f"<circle cx='160' cy='108' r='15' fill='{_PRIMARY_DARK}'/>"
            f"<circle cx='202' cy='92' r='17' fill='{_PRIMARY_DARK}'/>"
            f"<circle cx='244' cy='110' r='14' fill='{_PRIMARY_DARK}'/>"
        )
    if category == "Juguetes":
        return (
            f"<circle cx='156' cy='188' r='64' fill='{_PRIMARY}'/>"
            f"<path d='M156,124 A64,64 0 0 1 156,252' stroke='{_PRIMARY_DARK}' stroke-width='7' fill='none'/>"
            f"<path d='M110,156 A64,64 0 0 0 110,220' stroke='{_PRIMARY_DARK}' stroke-width='7' fill='none'/>"
            f"<rect x='252' y='216' width='80' height='24' rx='12' fill='{_ACCENT}'/>"
            f"<circle cx='248' cy='218' r='19' fill='{_ACCENT}'/>"
            f"<circle cx='248' cy='248' r='19' fill='{_ACCENT}'/>"
            f"<circle cx='320' cy='218' r='19' fill='{_ACCENT}'/>"
            f"<circle cx='320' cy='248' r='19' fill='{_ACCENT}'/>"
        )
    if category == "Higiene":
        return (
            f"<rect x='162' y='156' width='76' height='136' rx='18' fill='{_PRIMARY}'/>"
            f"<rect x='180' y='114' width='40' height='48' rx='9' fill='{_PRIMARY_DARK}'/>"
            f"<rect x='174' y='98' width='52' height='20' rx='7' fill='{_INK}'/>"
            f"<path d='M262,164 Q280,196 262,220 Q244,196 262,164 Z' fill='{_ACCENT}'/>"
        )
    if category == "Accesorios":
        return (
            f"<circle cx='200' cy='188' r='80' fill='none' stroke='{_PRIMARY}' stroke-width='28'/>"
            f"<rect x='178' y='252' width='44' height='36' rx='9' fill='{_ACCENT}'/>"
            f"<circle cx='200' cy='108' r='11' fill='{_PRIMARY_DARK}'/>"
        )
    if category == "Salud":
        return (
            f"<circle cx='200' cy='192' r='96' fill='{_ACCENT}' opacity='0.35'/>"
            f"<rect x='174' y='128' width='52' height='128' rx='16' fill='{_PRIMARY}'/>"
            f"<rect x='136' y='166' width='128' height='52' rx='16' fill='{_PRIMARY}'/>"
        )
    if category == "Medicamentos":
        return (
            f"<rect x='116' y='168' width='168' height='64' rx='32' fill='{_PRIMARY}'/>"
            f"<path d='M116,200 a32,32 0 0 1 32,-32 h48 v64 h-48 a32,32 0 0 1 -32,-32 Z' fill='{_PRIMARY_DARK}'/>"
            f"<rect x='272' y='268' width='22' height='60' rx='7' fill='{_ACCENT}'/>"
            f"<rect x='248' y='292' width='70' height='22' rx='7' fill='{_ACCENT}'/>"
        )
    return f"<circle cx='200' cy='200' r='92' fill='{_PRIMARY}'/>"


def image_url_for_category(category: str, sku: str) -> str:
    bg = _bg_for_sku(sku)
    icon = _icon_markup(category)
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'>"
        f"<rect x='8' y='8' width='384' height='384' rx='40' fill='{bg}'/>"
        f"{icon}</svg>"
    )
    return "data:image/svg+xml," + quote(svg)


# Icono generico de respaldo (huella de pata) para cualquier producto nuevo
# que no este en PRODUCTS (por ejemplo, uno agregado manualmente sin SKU
# conocido aqui).
FALLBACK_IMAGE_URL = image_url_for_category("__generic__", "fallback")

_SKU_CATEGORY = {sku: category for (_, sku, _, _, category) in PRODUCTS}


def image_url_for_sku(sku: str) -> str:
    category = _SKU_CATEGORY.get(sku)
    if category:
        return image_url_for_category(category, sku)
    return FALLBACK_IMAGE_URL


# Marca y tipo de mascota por SKU (perro, gato, ambas).
BRAND_BY_SKU = {
    "ALM-PER-001": "NutriCan", "ALM-PER-002": "NutriCan", "ALM-PER-003": "DentaCan",
    "ALM-GAT-001": "FelixGourmet", "ALM-GAT-002": "FelixGourmet",
    "JUG-001": "PlayPet", "JUG-002": "PlayPet", "JUG-003": "PlayPet",
    "HIG-001": "CleanPet", "HIG-002": "CleanPet", "HIG-003": "CleanPet", "HIG-004": "CleanPet",
    "ACC-001": "WalkPro", "ACC-002": "WalkPro",
    "ACC-003": "ComfyPet", "ACC-004": "ComfyPet", "ACC-005": "ComfyPet",
    "SAL-001": "VitaPet", "SAL-002": "VitaPet", "SAL-003": "VitaPet",
    "ALM-PER-004": "NutriCan", "ALM-GAT-003": "FelixGourmet", "ALM-PER-005": "NutriCan",
    "JUG-004": "PlayPet", "JUG-005": "PlayPet",
    "HIG-005": "CleanPet", "HIG-006": "CleanPet",
    "ACC-006": "WalkPro", "ACC-007": "ComfyPet", "ACC-008": "ComfyPet",
    "SAL-004": "VitaPet", "SAL-005": "VitaPet",
    "MED-001": "VetCare", "MED-002": "VetCare", "MED-003": "VetCare", "MED-004": "VetCare",
    "BRA-001": "Royal Canin", "BRA-002": "Hill's", "BRA-003": "Purina",
    "BRA-004": "Whiskas", "BRA-005": "Eukanuba", "BRA-006": "Pedigree",
    "BRA-007": "VetriScience", "BRA-008": "NexGard", "BRA-009": "Drontal",
}

PET_TYPE_BY_SKU = {
    "ALM-PER-001": "perro", "ALM-PER-002": "perro", "ALM-PER-003": "perro",
    "ALM-GAT-001": "gato", "ALM-GAT-002": "gato",
    "JUG-001": "perro", "JUG-002": "gato", "JUG-003": "perro",
    "HIG-001": "ambas", "HIG-002": "ambas", "HIG-003": "gato", "HIG-004": "ambas",
    "ACC-001": "perro", "ACC-002": "perro",
    "ACC-003": "ambas", "ACC-004": "ambas", "ACC-005": "ambas",
    "SAL-001": "ambas", "SAL-002": "perro", "SAL-003": "ambas",
    "ALM-PER-004": "perro", "ALM-GAT-003": "gato", "ALM-PER-005": "perro",
    "JUG-004": "gato", "JUG-005": "perro",
    "HIG-005": "ambas", "HIG-006": "ambas",
    "ACC-006": "ambas", "ACC-007": "ambas", "ACC-008": "gato",
    "SAL-004": "ambas", "SAL-005": "ambas",
    "MED-001": "perro", "MED-002": "gato", "MED-003": "ambas", "MED-004": "ambas",
    "BRA-001": "perro", "BRA-002": "perro", "BRA-003": "gato",
    "BRA-004": "gato", "BRA-005": "perro", "BRA-006": "perro",
    "BRA-007": "ambas", "BRA-008": "perro", "BRA-009": "perro",
}


def get_or_create_category(db, name, description):
    cat = db.query(Category).filter(Category.name == name).first()
    if cat:
        return cat
    cat = Category(name=name, description=description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    print(f"  + categoría creada: {name}")
    return cat


# Nombres de productos de prueba/duplicados que quedaron de pruebas manuales
# en el panel admin (no son parte del catálogo oficial de este script) y que
# se desactivan automáticamente para no confundir al cliente con duplicados.
LEGACY_DUPLICATE_NAMES = ["Croquetas Perro 5kg"]


def deactivate_legacy_duplicates(db):
    deactivated = 0
    for name in LEGACY_DUPLICATE_NAMES:
        matches = (
            db.query(Product)
            .filter(Product.name == name, Product.is_active == 1)
            .all()
        )
        for product in matches:
            product.is_active = 0
            deactivated += 1
            print(f"  - desactivado duplicado de prueba: {product.name} (sku={product.sku}, id={product.id})")
    if deactivated:
        db.commit()
    return deactivated


def main():
    db = SessionLocal()
    try:
        removed = deactivate_legacy_duplicates(db)
        if removed:
            print()

        categories_by_name = {}
        for name, description in CATEGORIES:
            categories_by_name[name] = get_or_create_category(db, name, description)

        created, updated, skipped = 0, 0, 0
        for name, sku, price, description, category_name in PRODUCTS:
            image_url = image_url_for_sku(sku)
            brand = BRAND_BY_SKU.get(sku)
            pet_type = PET_TYPE_BY_SKU.get(sku)
            existing = db.query(Product).filter(Product.sku == sku).first()
            if existing:
                changed = False
                if existing.image_url != image_url:
                    existing.image_url = image_url
                    changed = True
                if existing.brand != brand:
                    existing.brand = brand
                    changed = True
                if existing.pet_type != pet_type:
                    existing.pet_type = pet_type
                    changed = True
                if changed:
                    db.commit()
                    updated += 1
                    print(f"  ~ datos actualizados: {name} ({sku})")
                else:
                    skipped += 1
                continue

            product = Product(
                name=name,
                description=description,
                price=price,
                sku=sku,
                image_url=image_url,
                brand=brand,
                pet_type=pet_type,
                is_active=1,
                categories=[categories_by_name[category_name]],
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            inventory_service.create_inventory_for_product(db, product.id)
            inventory_service.adjust_stock(db, product.id, delta=50)  # stock inicial de demo
            created += 1
            print(f"  + producto creado: {name} ({sku})")

        print()
        print(f"Listo. Productos creados: {created}, imágenes actualizadas: {updated}, sin cambios: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
