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
    # cualquier catalogo); las fotos siguen siendo fotografia de stock
    # generica de Unsplash (no son fotos oficiales de empaques de esas
    # marcas), igual que el resto del catalogo.
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

# Foto real de Unsplash elegida a mano para cada SKU, para que la imagen
# corresponda a lo que el producto realmente es (comida de perro, juguete
# de gato, correa, pastillero, etc.) en vez de una foto genérica sin relación.
_IMG = "?w=400&h=300&fit=crop&auto=format&q=60"
IMAGE_URLS = {
    # --- Fotos actualizadas: se reemplazaron las que mostraban un entorno
    # ("lifestyle": perro en el parque, persona paseando, etc.) por close-ups
    # centrados en el producto mismo, a pedido explicito del cliente. Las
    # que no tienen un reemplazo de producto-solo disponible en Unsplash
    # (banco de fotos gratuito, sin cobertura completa de este nicho) se
    # dejaron como estaban; para esos casos puntuales lo ideal es que subas
    # tu propia foto del producto real desde "Editar" en el panel admin
    # (campo "URL de imagen").
    "ALM-PER-001": f"https://images.unsplash.com/photo-1684882726821-2999db517441{_IMG}",  # bolsa de alimento seco para perro, de cerca
    "ALM-PER-002": f"https://images.unsplash.com/photo-1767023023369-96a7c923be0c{_IMG}",  # perro comiendo de su tazón (sin reemplazo de producto-solo disponible)
    "ALM-GAT-001": f"https://images.unsplash.com/photo-1520811607976-6d7812b0ecac{_IMG}",  # gatos comiendo (sin reemplazo de producto-solo disponible)
    "ALM-GAT-002": f"https://images.unsplash.com/photo-1695169954725-fa757fd7315c{_IMG}",  # bowl de croquetas de cerca, sin mascota
    "ALM-PER-003": f"https://images.unsplash.com/photo-1709810024789-4519a14f05ae{_IMG}",  # empaques de snacks para perro, solos
    "JUG-001": f"https://images.unsplash.com/photo-1586016008569-4e1d76657ede{_IMG}",  # pelota sola, de cerca, sin perro
    "JUG-002": f"https://images.unsplash.com/photo-1723462476788-a8f60eb78658{_IMG}",  # gato jugando con juguete (sin reemplazo de producto-solo disponible)
    "JUG-003": f"https://images.unsplash.com/photo-1522008693277-086ad6075b78{_IMG}",  # perro mordiendo una cuerda (sin reemplazo de producto-solo disponible)
    "HIG-001": f"https://images.unsplash.com/photo-1747858989102-cca0f4dc4a11{_IMG}",  # botella de shampoo sola, fondo neutro
    "HIG-002": f"https://plus.unsplash.com/premium_photo-1677234147226-b6864587aa40{_IMG}",  # limpieza con toallitas/paño (sin reemplazo de producto-solo disponible)
    "HIG-003": f"https://images.unsplash.com/photo-1659205143781-a6e263c4aadf{_IMG}",  # gato junto a su caja (sin reemplazo de producto-solo disponible)
    "HIG-004": f"https://images.unsplash.com/photo-1528846104175-4fd300ee59da{_IMG}",  # cepillando el pelo de un perro (sin reemplazo de producto-solo disponible)
    "ACC-001": f"https://images.unsplash.com/photo-1704770064081-07d189b95b10{_IMG}",  # perro con correa (no se encontro foto de producto-solo confiable; recomendado subir foto propia)
    "ACC-002": f"https://images.unsplash.com/photo-1673069783560-6d4094285be4{_IMG}",  # primer plano de collar (no se encontro foto de producto-solo confiable; recomendado subir foto propia)
    "ACC-003": f"https://images.unsplash.com/photo-1708303364738-48188a0e050f{_IMG}",  # perro pequeño en su cama (sin reemplazo de producto-solo disponible)
    "ACC-004": f"https://images.unsplash.com/photo-1778856582851-9da9e3a1a831{_IMG}",  # transportadora sola, sin mascota
    "ACC-005": f"https://images.unsplash.com/photo-1632236568054-12f36ecee2f6{_IMG}",  # perro comiendo de comedero (sin reemplazo de producto-solo disponible)
    "SAL-001": f"https://images.unsplash.com/photo-1631669969504-f35518bf96ba{_IMG}",  # frasco de tabletas, solo
    "SAL-002": f"https://plus.unsplash.com/premium_photo-1683134036144-82b0a3d50f11{_IMG}",  # perro en clínica veterinaria (sin reemplazo de producto-solo disponible)
    "SAL-003": f"https://images.unsplash.com/photo-1763668331599-487470fb85b2{_IMG}",  # frasco de cápsulas, solo
    "ALM-PER-004": f"https://images.unsplash.com/photo-1671900602295-3cf4fbc121d2{_IMG}",  # perro grande adulto/mayor
    "ALM-GAT-003": f"https://images.unsplash.com/photo-1707642013416-6d7362adc46e{_IMG}",  # gato junto a bolsa de premios
    "ALM-PER-005": f"https://images.unsplash.com/photo-1632236568054-12f36ecee2f6{_IMG}",  # perro comiendo de su tazón
    "JUG-004": f"https://images.unsplash.com/photo-1731315900916-bed2a2ebb856{_IMG}",  # gato jugando con juguete de cuerda
    "JUG-005": f"https://images.unsplash.com/photo-1535294435445-d7249524ef2e{_IMG}",  # hueso de juguete solo, sobre superficie neutra
    "HIG-005": f"https://images.unsplash.com/photo-1763631403216-8d193008481e{_IMG}",  # frasco de colonia solo, fondo neutro
    "HIG-006": f"https://images.unsplash.com/photo-1765464281325-d9bae89108dc{_IMG}",  # cortaúñas solos, fondo blanco
    "ACC-006": f"https://images.unsplash.com/photo-1673069783560-6d4094285be4{_IMG}",  # collar con placa (sin reemplazo de producto-solo disponible)
    "ACC-007": f"https://images.unsplash.com/photo-1541887796712-054f4b0f8e5d{_IMG}",  # perro bebiendo de dispensador portátil (sin reemplazo de producto-solo disponible)
    "ACC-008": f"https://images.unsplash.com/photo-1724023838952-a12ba4b36a8a{_IMG}",  # gato en su rascador (sin reemplazo de producto-solo disponible)
    "SAL-004": f"https://images.unsplash.com/photo-1670850756988-a1943aa0e554{_IMG}",  # botella de aceite/cápsulas blandas, sola
    "SAL-005": f"https://images.unsplash.com/photo-1760024888924-0bb9b5181f8e{_IMG}",  # sobres de suplemento en caja, solos
    "MED-001": f"https://images.unsplash.com/photo-1789983361998-1cf433741217{_IMG}",  # blíster de comprimidos, solo
    "MED-002": f"https://images.unsplash.com/photo-1776107490671-4be91775c558{_IMG}",  # blíster de comprimidos (distinto), solo
    "MED-003": f"https://plus.unsplash.com/premium_photo-1683134036144-82b0a3d50f11{_IMG}",  # atención veterinaria (sin reemplazo de producto-solo disponible)
    "MED-004": f"https://images.unsplash.com/photo-1638609927040-8a7e97cd9d6a{_IMG}",  # tubo de pomada/crema, solo
    # --- Productos de marcas reconocidas ---
    "BRA-001": f"https://images.unsplash.com/photo-1764249453874-46864677b10e{_IMG}",  # croquetas secas de cerca (foto generica, marca es solo texto)
    "BRA-002": f"https://images.unsplash.com/photo-1764249453874-46864677b10e{_IMG}",  # croquetas secas de cerca
    "BRA-003": f"https://images.unsplash.com/photo-1695169954725-fa757fd7315c{_IMG}",  # bowl de croquetas de cerca
    "BRA-004": f"https://images.unsplash.com/photo-1695169954725-fa757fd7315c{_IMG}",  # bowl de croquetas de cerca
    "BRA-005": f"https://images.unsplash.com/photo-1764249453874-46864677b10e{_IMG}",  # croquetas secas de cerca
    "BRA-006": f"https://images.unsplash.com/photo-1568640347023-a616a30bc3bd{_IMG}",  # snack dental, solo
    "BRA-007": f"https://images.unsplash.com/photo-1700911772670-410b44ac7392{_IMG}",  # frasco de multivitamínico, solo
    "BRA-008": f"https://images.unsplash.com/photo-1714642764170-fb950305c397{_IMG}",  # blíster de comprimidos, solo
    "BRA-009": f"https://images.unsplash.com/photo-1714642764170-fb950305c397{_IMG}",  # blíster de comprimidos, solo
}

# Foto genérica de respaldo para cualquier producto nuevo que no esté en
# IMAGE_URLS (por ejemplo, uno agregado manualmente sin SKU conocido aquí).
FALLBACK_IMAGE_URL = f"https://plus.unsplash.com/premium_photo-1729111978398-821b4930c4c2{_IMG}"


def image_url_for_sku(sku: str) -> str:
    return IMAGE_URLS.get(sku, FALLBACK_IMAGE_URL)


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
