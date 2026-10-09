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
    "JUG-003": f"https://images.unsplash.com/photo-1718159610145-eb0f3a1fe39a{_IMG}",  # perro con juguete en el hocico
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
}

# Foto genérica de respaldo para cualquier producto nuevo que no esté en
# IMAGE_URLS (por ejemplo, uno agregado manualmente sin SKU conocido aquí).
FALLBACK_IMAGE_URL = f"https://plus.unsplash.com/premium_photo-1729111978398-821b4930c4c2{_IMG}"


def image_url_for_sku(sku: str) -> str:
    return IMAGE_URLS.get(sku, FALLBACK_IMAGE_URL)


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


def main():
    db = SessionLocal()
    try:
        categories_by_name = {}
        for name, description in CATEGORIES:
            categories_by_name[name] = get_or_create_category(db, name, description)

        created, updated, skipped = 0, 0, 0
        for name, sku, price, description, category_name in PRODUCTS:
            image_url = image_url_for_sku(sku)
            existing = db.query(Product).filter(Product.sku == sku).first()
            if existing:
                if existing.image_url != image_url:
                    existing.image_url = image_url
                    db.commit()
                    updated += 1
                    print(f"  ~ imagen actualizada: {name} ({sku})")
                else:
                    skipped += 1
                continue

            product = Product(
                name=name,
                description=description,
                price=price,
                sku=sku,
                image_url=image_url,
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
