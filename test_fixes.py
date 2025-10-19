"""
Script de prueba para verificar las correcciones de datos fantasma
Ejecutar: python test_fixes.py
"""

import sqlite3
from datetime import datetime

def test_database():
    """Verifica el estado de la base de datos"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('barberia.db')
        cursor = conn.cursor()
        
        # Verificar clientes
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clientes = cursor.fetchone()[0]
        print(f"\n👥 Total de clientes: {total_clientes}")
        
        if total_clientes > 0:
            cursor.execute("SELECT name, phone, created_at FROM clients ORDER BY created_at DESC LIMIT 5")
            clientes = cursor.fetchall()
            print("\n📋 Últimos 5 clientes:")
            for nombre, telefono, fecha in clientes:
                print(f"   - {nombre} ({telefono}) - Creado: {fecha}")
        
        # Verificar ventas
        cursor.execute("SELECT COUNT(*) FROM sales")
        total_ventas = cursor.fetchone()[0]
        print(f"\n🧾 Total de ventas: {total_ventas}")
        
        if total_ventas > 0:
            cursor.execute("""
                SELECT s.ts, c.name, i.name, s.quantity 
                FROM sales s 
                LEFT JOIN clients c ON s.client_id = c.id
                LEFT JOIN items i ON s.item_id = i.id
                ORDER BY s.ts DESC LIMIT 5
            """)
            ventas = cursor.fetchall()
            print("\n📋 Últimas 5 ventas:")
            for fecha, cliente, item, cantidad in ventas:
                cliente_str = cliente if cliente else "(sin cliente)"
                print(f"   - {fecha}: {cliente_str} - {item} (x{cantidad})")
        
        # Verificar duplicados
        cursor.execute("""
            SELECT client_id, DATE(ts), item_id, COUNT(*) as count
            FROM sales
            GROUP BY client_id, DATE(ts), item_id
            HAVING count > 1
        """)
        duplicados = cursor.fetchall()
        
        if duplicados:
            print(f"\n⚠️ ADVERTENCIA: Se encontraron {len(duplicados)} grupos de ventas duplicadas:")
            for client_id, fecha, item_id, count in duplicados:
                print(f"   - Cliente ID {client_id}, Fecha {fecha}, Item ID {item_id}: {count} registros")
            print("\n💡 Ejecuta la herramienta de deduplicación en Configuración")
        else:
            print("\n✅ No se encontraron ventas duplicadas")
        
        # Verificar gastos
        cursor.execute("SELECT COUNT(*) FROM expenses")
        total_gastos = cursor.fetchone()[0]
        print(f"\n💸 Total de gastos: {total_gastos}")
        
        # Verificar tabla de configuración
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_config'")
        if cursor.fetchone():
            print("\n✅ Tabla app_config existe")
            cursor.execute("SELECT key, value FROM app_config")
            configs = cursor.fetchall()
            if configs:
                print("📋 Configuraciones guardadas:")
                for key, value in configs:
                    print(f"   - {key}: {value}")
        else:
            print("\n⚠️ Tabla app_config no existe (se creará al iniciar la app)")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"\n❌ Error al acceder a la base de datos: {e}")
        print("💡 Asegúrate de que barberia.db existe en el directorio actual")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

def test_code_syntax():
    """Verifica que no haya errores de sintaxis en app.py"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICACIÓN DE SINTAXIS")
    print("=" * 60)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'app.py', 'exec')
        print("\n✅ No se encontraron errores de sintaxis en app.py")
        
        # Verificar que seed_sample_data esté comentado
        if '# seed_sample_data()' in code:
            print("✅ seed_sample_data() está correctamente deshabilitado")
        else:
            print("⚠️ ADVERTENCIA: seed_sample_data() podría estar activo")
        
        # Verificar que existan las nuevas funciones
        funciones_requeridas = [
            'get_config_value',
            'set_config_value',
            'clean_all_data',
            'remove_duplicate_sales',
            'class AppConfig'
        ]
        
        print("\n📋 Verificando nuevas funcionalidades:")
        for funcion in funciones_requeridas:
            if funcion in code:
                print(f"   ✅ {funcion} encontrada")
            else:
                print(f"   ❌ {funcion} NO encontrada")
        
    except SyntaxError as e:
        print(f"\n❌ Error de sintaxis en app.py:")
        print(f"   Línea {e.lineno}: {e.msg}")
    except FileNotFoundError:
        print("\n❌ No se encontró el archivo app.py")
        print("💡 Ejecuta este script desde el directorio de la aplicación")
    except Exception as e:
        print(f"\n❌ Error al verificar sintaxis: {e}")

def show_recommendations():
    """Muestra recomendaciones para el usuario"""
    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES")
    print("=" * 60)
    print("""
1. 🗑️ Si tienes datos fantasma actuales:
   - Abre la app: streamlit run app.py
   - Ve a Configuración → Diagnóstico y Mantenimiento
   - Usa "Buscar y Eliminar Duplicados"
   - Si es necesario, usa "Limpieza Total"

2. 🔄 Después de limpiar:
   - Recarga la página (F5)
   - Limpia caché del navegador (Ctrl+Shift+Delete)
   - Cierra y reabre la aplicación

3. ✅ Para verificar que todo funciona:
   - Ve a Clientes y verifica que no haya Juan, Miguel, José
   - Ve a Historial y verifica que no haya datos de 10/10, 11/10, 12/10
   - Recarga varias veces y confirma que no reaparecen

4. 🧪 Para generar datos de prueba en el futuro:
   - Ve a Configuración → Datos de Prueba
   - Usa el botón "Generar Datos de Prueba"
   - Esto es MANUAL y controlado por ti

5. 📖 Lee el archivo SOLUCION_DATOS_FANTASMA.md para más detalles
""")

if __name__ == "__main__":
    print("\n🔧 TEST DE CORRECCIONES - DATOS FANTASMA\n")
    
    test_code_syntax()
    test_database()
    show_recommendations()
    
    print("\n✅ Pruebas completadas. Revisa los resultados arriba.\n")
