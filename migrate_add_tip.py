"""
Script de migración para agregar la columna 'tip' a la tabla 'sales'
Ejecutar este script una sola vez antes de usar la aplicación con la nueva funcionalidad de propinas.
"""

import sqlite3
import os

# Ruta a la base de datos
DB_PATH = "barberia.db"

def migrate_add_tip_column():
    """Agrega la columna 'tip' a la tabla 'sales' si no existe"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró la base de datos en {DB_PATH}")
        print("La columna 'tip' se creará automáticamente cuando inicies la aplicación.")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna 'tip' ya existe
        cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tip' in columns:
            print("✅ La columna 'tip' ya existe en la tabla 'sales'.")
        else:
            # Agregar la columna 'tip'
            cursor.execute("ALTER TABLE sales ADD COLUMN tip REAL DEFAULT 0.0")
            conn.commit()
            print("✅ Columna 'tip' agregada exitosamente a la tabla 'sales'.")
        
        # Cerrar conexión
        conn.close()
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Iniciando migración de base de datos...")
    migrate_add_tip_column()
    print("✅ Migración completada.")
    print("\n💡 Ahora puedes ejecutar la aplicación normalmente con: streamlit run app.py")
