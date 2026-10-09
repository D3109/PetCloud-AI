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
]

# Foto real de Unsplash elegida a mano para cada SKU, para que la imagen
# corresponda a lo que el producto realmente es (comida de perro, juguete
# de gato, correa, pastillero, etc.) en vez de una foto genérica sin relación.
_IMG = "?w=400&h=300&fit=crop&auto=format&q=60"
IMAGE_URLS = {
    "ALM-PER-001": f"https://images.unsplash.com/photo-1676193866128-03a926df76ef{_IMG}",  # tazón con comida de perro
    "ALM-PER-002": f"https://images.unsplash.com/photo-1767023023369-96a7c923be0c{_IMG}",  # perro comiendo de su tazón
    "ALM-GAT-001": f"https://images.unsplash.com/photo-1520811607976-6d7812b0ecac{_IMG}",  # gatos comiendo
    "ALM-GAT-002": f"https://images.unsplash.com/photo-1764249453874-46864677b10e{_IMG}",  # croquetas secas de cerca
    "ALM-PER-003": f"https://images.unsplash.com/photo-1488569098285-adeecb95641f{_IMG}",  # dándole premio/snack a un perro
    "JUG-001": f"https://images.unsplash.com/photo-1696416806113-1f247ff0eb5c{_IMG}",  # perro con pelota en el hocico
    "JUG-002": f"https://images.unsplash.com/photo-1723462476788-a8f60eb78658{_IMG}",  # gato jugando con juguete
    "JUG-003": f"https://images.unsplash.com/photo-1522008693277-086ad6075b78{_IMG}",  # perro mordiendo una cuerda
    "HIG-001": f"https://images.unsplash.com/photo-1597603413826-cd1c06b05222{_IMG}",  # perro pequeño (baño/higiene)
    "HIG-002": f"https://images.unsplash.com/photo-1597603413826-cd1c06b05222{_IMG}",  # perro pequeño (higiene/limpieza)
    "HIG-003": f"https://images.unsplash.com/photo-1659205143781-a6e263c4aadf{_IMG}",  # gato junto a su caja
    "HIG-004": f"https://images.unsplash.com/photo-1528846104175-4fd300ee59da{_IMG}",  # cepillando el pelo de un perro
    "ACC-001": f"https://images.unsplash.com/photo-1704770064081-07d189b95b10{_IMG}",  # perro con correa
    "ACC-002": f"https://images.unsplash.com/photo-1673069783560-6d4094285be4{_IMG}",  # primer plano de collar
    "ACC-003": f"https://images.unsplash.com/photo-1708303364738-48188a0e050f{_IMG}",  # perro pequeño en su cama
    "ACC-004": f"https://images.unsplash.com/photo-1527150602-a98f7a6f2746{_IMG}",  # transportadora de mascota
    "ACC-005": f"https://images.unsplash.com/photo-1632236568054-12f36ecee2f6{_IMG}",  # perro comiendo de comedero
    "SAL-001": f"https://images.unsplash.com/photo-1644432757359-b184377d9eb0{_IMG}",  # tabletas/vitaminas
    "SAL-002": f"https://plus.unsplash.com/premium_photo-1683134036144-82b0a3d50f11{_IMG}",  # perro en clínica veterinaria
    "SAL-003": f"https://plus.unsplash.com/premium_photo-1668605109201-2dcf7a001215{_IMG}",  # pastillero con cápsulas
    "ALM-PER-004": f"https://images.unsplash.com/photo-1671900602295-3cf4fbc121d2{_IMG}",  # perro grande adulto/mayor
    "ALM-GAT-003": f"https://images.unsplash.com/photo-1707642013416-6d7362adc46e{_IMG}",  # gato junto a bolsa de premios
    "ALM-PER-005": f"https://images.unsplash.com/photo-1632236568054-12f36ecee2f6{_IMG}",  # perro comiendo de su tazón
    "JUG-004": f"https://images.unsplash.com/photo-1731315900916-bed2a2ebb856{_IMG}",  # gato jugando con juguete de cuerda
    "JUG-005": f"https://images.unsplash.com/photo-1690876821657-1fe926211657{_IMG}",  # perro mordiendo un hueso/palo
    "HIG-005": f"https://images.unsplash.com/photo-1760920250029-36af9369a0bb{_IMG}",  # frasco de colonia
    "HIG-006": f"https://images.unsplash.com/photo-1528846104175-4fd300ee59da{_IMG}",  # cuidado/aseo de un perro
    "ACC-006": f"https://images.unsplash.com/photo-1673069783560-6d4094285be4{_IMG}",  # collar con placa
    "ACC-007": f"https://images.unsplash.com/photo-1541887796712-054f4b0f8e5d{_IMG}",  # perro bebiendo de dispensador portátil
    "ACC-008": f"https://images.unsplash.com/photo-1724023838952-a12ba4b36a8a{_IMG}",  # gato en su rascador
    "SAL-004": f"https://images.unsplash.com/photo-1644432757359-b184377d9eb0{_IMG}",  # cápsulas/suplemento
    "SAL-005": f"https://plus.unsplash.com/premium_photo-1668605109201-2dcf7a001215{_IMG}",  # sobres/pastillero
    "MED-001": f"https://images.unsplash.com/photo-1711265767477-924313b833c5{_IMG}",  # comprimidos/tabletas
    "MED-002": f"https://images.unsplash.com/photo-1711265767477-924313b833c5{_IMG}",  # comprimidos/tabletas
    "MED-003": f"https://plus.unsplash.com/premium_photo-1683134036144-82b0a3d50f11{_IMG}",  # atención veterinaria
    "MED-004": f"https://plus.unsplash.com/premium_photo-1679106767239-95b814bf9795{_IMG}",  # pomada/crema en tubo
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
