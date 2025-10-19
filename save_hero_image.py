"""
Script para guardar la imagen del hero.
Coloca la imagen 'hero_image.png' en la carpeta static/
"""
import os
import shutil

# Ruta de destino
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

print("📁 Carpeta 'static' lista")
print(f"📍 Ruta: {static_dir}")
print("\n✅ Por favor, coloca tu imagen PNG en:")
print(f"   {os.path.join(static_dir, 'hero_image.png')}")
print("\n💡 La imagen debe llamarse: hero_image.png")
