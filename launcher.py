#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher para la aplicación de Barbería
Este archivo se convierte a .exe para facilitar el uso
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

def find_python():
    """Encuentra el ejecutable de Python"""
    python_commands = ['python', 'python3', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def check_dependencies():
    """Verifica si las dependencias están instaladas"""
    try:
        import streamlit
        import pandas
        import sqlalchemy
        import plotly
        return True
    except ImportError:
        return False

def install_dependencies():
    """Instala las dependencias necesarias"""
    python_cmd = find_python()
    if not python_cmd:
        print("❌ ERROR: Python no encontrado")
        return False
    
    print("📦 Instalando dependencias...")
    try:
        # Instalar desde requirements.txt
        result = subprocess.run([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              check=True, capture_output=True, text=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        print(f"Salida del error: {e.stderr}")
        return False

def open_browser_delayed():
    """Abre el navegador después de un retraso"""
    time.sleep(3)  # Esperar 3 segundos para que Streamlit se inicie
    webbrowser.open('http://localhost:8501')

def main():
    """Función principal del launcher"""
    print("=" * 50)
    print("🏪 BARBERÍA - SISTEMA DE GESTIÓN")
    print("=" * 50)
    print()
    
    # Cambiar al directorio del script
    if getattr(sys, 'frozen', False):
        # Si estamos ejecutando desde un .exe
        script_dir = Path(sys.executable).parent.absolute()
    else:
        # Si estamos ejecutando el .py directamente
        script_dir = Path(__file__).parent.absolute()
    
    os.chdir(script_dir)
    print(f"📂 Directorio de trabajo: {script_dir}")
    
    # Verificar si app.py existe
    if not Path('app.py').exists():
        print("❌ ERROR: No se encuentra el archivo app.py")
        print("Asegúrate de que app.py esté en la misma carpeta que este ejecutable")
        input("Presiona Enter para salir...")
        return
    
    # Verificar Python
    python_cmd = find_python()
    if not python_cmd:
        print("❌ ERROR: Python no está instalado o no está en el PATH")
        print("Por favor instala Python desde: https://python.org")
        input("Presiona Enter para salir...")
        return
    
    print(f"✅ Python encontrado: {python_cmd}")
    
    # Verificar dependencias
    if not check_dependencies():
        print("📦 Instalando dependencias necesarias...")
        if not install_dependencies():
            print("❌ No se pudieron instalar las dependencias")
            input("Presiona Enter para salir...")
            return
    else:
        print("✅ Todas las dependencias están instaladas")
    
    print()
    print("🚀 Iniciando aplicación...")
    print("⚠️  IMPORTANTE:")
    print("   - NO cierres esta ventana mientras uses la aplicación")
    print("   - La aplicación se abrirá automáticamente en tu navegador")
    print("   - Si no se abre, ve manualmente a: http://localhost:8501")
    print("   - Para cerrar: Ctrl+C en esta ventana")
    print()
    print("=" * 50)
    
    try:
        # Abrir navegador en un hilo separado
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Ejecutar Streamlit
        cmd = [python_cmd, '-m', 'streamlit', 'run', 'app.py', 
               '--server.headless', 'true', 
               '--server.port', '8501',
               '--server.address', 'localhost']
        
        process = subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando la aplicación: {e}")
    
    print("\n👋 ¡Hasta luego!")
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
