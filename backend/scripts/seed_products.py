"""Carga categorias y productos de ejemplo para PetCloud IA.

Uso (desde backend/, con el entorno virtual / dependencias activas):
    python3 scripts/seed_products.py

Es idempotente: si una categoria o un SKU ya existe, no lo duplica.
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

        created, skipped = 0, 0
        for name, sku, price, description, category_name in PRODUCTS:
            existing = db.query(Product).filter(Product.sku == sku).first()
            if existing:
                skipped += 1
                continue

            product = Product(
                name=name,
                description=description,
                price=price,
                sku=sku,
                image_url=f"https://picsum.photos/seed/{sku}/400/300",
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
        print(f"Listo. Productos creados: {created}, ya existían: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
