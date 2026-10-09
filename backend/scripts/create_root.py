"""Crea (o promueve a) el usuario ROOT / superadministrador de PetCloud IA.

Este es el UNICO lugar del sistema donde se puede asignar el rol "root":
no existe ningun endpoint HTTP que lo permita, ni el formulario público de
registro ni el panel de administrador pueden crear o ascender a un ROOT.
Esto evita que alguien se vuelva superadministrador por accidente o por un
fallo de seguridad en la API.

Uso (desde backend/, con el entorno virtual / dependencias activas):

    ROOT_EMAIL="tu-correo@dominio.com" ROOT_PASSWORD="una-contraseña-fuerte" \
        python3 scripts/create_root.py

Si no se dan las variables de entorno, el script las pide de forma
interactiva (la contraseña no se muestra en pantalla).

Comportamiento:
  - Si el correo no existe: crea un usuario nuevo con rol "root".
  - Si el correo ya existe: lo asciende a rol "root" (útil para convertir tu
    propia cuenta de administrador en la cuenta ROOT inicial).
  - Si ya existe otro usuario con rol "root", el script lo avisa y pide
    confirmación antes de crear un segundo ROOT (normalmente solo debe
    haber uno).
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        existing_root = db.query(User).filter(User.role == "root").first()
        if existing_root:
            print(f"Ya existe un usuario ROOT: {existing_root.email}")
            confirm = input("¿Quieres crear/ascender otro de todas formas? [s/N]: ").strip().lower()
            if confirm != "s":
                print("Cancelado.")
                return

        email = os.environ.get("ROOT_EMAIL") or input("Correo del usuario ROOT: ").strip()
        password = os.environ.get("ROOT_PASSWORD") or getpass.getpass("Contraseña del usuario ROOT: ")

        if not email or not password:
            print("Correo y contraseña son obligatorios. Cancelado.")
            return
        if len(password) < 8:
            print("La contraseña debe tener al menos 8 caracteres. Cancelado.")
            return

        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = "root"
            user.is_active = 1
            db.commit()
            print(f"Usuario existente '{email}' ascendido a ROOT.")
        else:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                full_name="Super Administrador",
                role="root",
                is_active=1,
            )
            db.add(user)
            db.commit()
            print(f"Usuario ROOT '{email}' creado correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
