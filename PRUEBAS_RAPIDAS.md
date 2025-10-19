# 🧪 Pruebas Rápidas - Historial y Resumen

## ✅ Checklist de Verificación

### **1. Iniciar la Aplicación**

```bash
streamlit run app.py
```

**Verificar en consola**:
- ✅ "✅ Columna 'ticket_id' agregada exitosamente..."
- ✅ "🔄 Agrupando ventas existentes por visita..."
- ✅ "✅ X ventas agrupadas en Y visitas."

---

### **2. Probar Historial Consolidado**

#### **Paso 1**: Ir a 📜 Historial

**Verificar**:
- [ ] Título dice "📜 Historial de Visitas"
- [ ] Subtítulo explica agrupación
- [ ] Muestra "Total de visitas: X"

#### **Paso 2**: Expandir una visita

**Verificar**:
- [ ] Título muestra: Fecha + Hora + Cliente + Total
- [ ] Badges de servicios visibles (azul para servicios, verde para productos)
- [ ] Tabla de detalle con columnas: Servicio/Producto, Cant., Precio Unit., Descuento, Subtotal
- [ ] Panel derecho muestra: Total, Cliente, Fecha, Hora, N° Servicios

#### **Paso 3**: Verificar agrupación

**Caso de prueba**:
1. Buscar cliente "Nicolás Villar" en fecha 2025-10-12
2. Debe mostrar UNA sola visita con:
   - Corte de pelo x1
   - Perfilado de cejas x1
3. Total: $ 9.000

**Resultado esperado**: ✅ Una fila, no dos filas separadas

---

### **3. Probar Resumen (antes Dashboard)**

#### **Paso 1**: Ir a 📊 Resumen

**Verificar**:
- [ ] Título dice "📊 Resumen" (NO "Dashboard")
- [ ] Selector "🔍 Mostrar:" visible arriba a la derecha
- [ ] Por defecto muestra: KPIs y Distribución

#### **Paso 2**: Probar KPIs

**Verificar**:
- [ ] Sección "📈 Indicadores Clave" visible
- [ ] 3 métricas: Hoy, Esta Semana, Este Mes
- [ ] Valores calculados correctamente

#### **Paso 3**: Probar Distribución

**Verificar**:
- [ ] Sección "💼 Distribución de Ingresos" visible
- [ ] Gráfico de torta (donut) con 4 categorías:
  - 💼 Sueldo
  - 🏪 Barbería
  - 💰 Ahorro
  - 📈 Inversión
- [ ] Tabla de detalle con porcentajes y montos
- [ ] Mensaje: "Puedes ajustar los porcentajes en Configuración"

#### **Paso 4**: Probar Selector de Vista

**Acciones**:
1. Desmarcar "KPIs"
2. Verificar que KPIs desaparecen
3. Marcar "Top Servicios"
4. Verificar que aparece lista de top 5 servicios
5. Recargar página (F5)
6. Verificar que selección se mantiene

**Resultado esperado**: ✅ Widgets aparecen/desaparecen según selección

---

### **4. Probar Registro de Venta**

#### **Paso 1**: Ir a 🧾 Registrar venta

**Acciones**:
1. Seleccionar cliente existente o crear nuevo
2. Marcar múltiples servicios:
   - Corte de pelo
   - Perfilado de cejas
3. Hacer clic en "Guardar todo"

**Verificar**:
- [ ] Mensaje: "✅ Venta registrada correctamente"
- [ ] Mensaje: "📋 Ticket ID: xxxxxxxx... (2 servicios/productos)"
- [ ] Ticket ID mostrado (primeros 8 caracteres)

#### **Paso 2**: Verificar en Historial

**Acciones**:
1. Ir a 📜 Historial
2. Buscar la venta recién creada

**Verificar**:
- [ ] Aparece como UNA sola visita
- [ ] Muestra ambos servicios en badges
- [ ] Total es la suma de ambos servicios

---

### **5. Probar Configuración de Distribución**

#### **Paso 1**: Ir a ⚙️ Configuración

**Acciones**:
1. Buscar "📊 Reparto de Ingresos"
2. Cambiar porcentajes:
   - Sueldo: 40%
   - Barbería: 30%
   - Ahorro: 20%
   - Inversión: 10%
3. Guardar

**Verificar**:
- [ ] Mensaje: "Porcentajes guardados correctamente ✅"
- [ ] Suma = 100%

#### **Paso 2**: Verificar cambios en Resumen

**Acciones**:
1. Ir a 📊 Resumen
2. Ver sección "Distribución"

**Verificar**:
- [ ] Gráfico actualizado con nuevos porcentajes
- [ ] Tabla muestra nuevos valores
- [ ] Cálculos correctos

---

### **6. Casos Límite**

#### **Caso 1**: Dos visitas del mismo cliente el mismo día

**Setup**:
1. Registrar venta para "Juan" a las 10:00
   - Corte de pelo
2. Registrar venta para "Juan" a las 16:00 (6 horas después)
   - Perfilado de barba

**Resultado esperado**:
- [ ] DOS visitas separadas (superan ventana de 90 min)
- [ ] Cada una con su propio ticket_id

#### **Caso 2**: Servicios repetidos en la misma visita

**Setup**:
1. Registrar venta con:
   - Cera para peinar x2
   - Polvo texturizador x1

**Resultado esperado**:
- [ ] Una visita con 2 items
- [ ] Cera muestra "x2" en badge
- [ ] Total = (precio_cera × 2) + precio_polvo

#### **Caso 3**: Cliente sin nombre

**Setup**:
1. Registrar venta sin seleccionar cliente
2. Agregar servicio

**Resultado esperado**:
- [ ] Venta se registra correctamente
- [ ] En Historial aparece como "(sin cliente)"

---

### **7. Exportación CSV**

#### **Paso 1**: Ir a 📜 Historial

**Acciones**:
1. Hacer clic en "📥 Descargar Historial (CSV)"
2. Abrir archivo descargado

**Verificar**:
- [ ] Columnas: Fecha, Hora, Cliente, Servicios, Total
- [ ] Servicios en formato: "Corte de pelo (x1) + Perfilado de cejas (x1)"
- [ ] Una fila por visita (no por servicio individual)

---

### **8. Responsividad**

#### **En Desktop**:
- [ ] Selector de vista visible
- [ ] Gráfico de distribución en 2 columnas
- [ ] Historial con detalles expandibles

#### **En Móvil** (reducir ventana):
- [ ] Selector de vista se adapta
- [ ] Gráfico de distribución apilado verticalmente
- [ ] Badges de servicios se ajustan
- [ ] Tablas scrolleables

---

## 🐛 Problemas Comunes y Soluciones

### **Problema 1**: No veo la columna ticket_id

**Solución**:
```bash
# Verificar en base de datos
sqlite3 barberia.db "PRAGMA table_info(sales);"

# Si no existe, reiniciar app
Ctrl + C
streamlit run app.py
```

### **Problema 2**: Visitas no se agrupan

**Causa**: Migración no ejecutada

**Solución**:
```bash
# Revisar logs en consola
# Debe mostrar: "✅ X ventas agrupadas en Y visitas"

# Si no aparece, eliminar y recrear DB
copy barberia.db barberia_backup.db
del barberia.db
streamlit run app.py
```

### **Problema 3**: Distribución no muestra gráfico

**Causa**: No hay ingresos en el período

**Solución**:
1. Ajustar filtros de fecha (sidebar)
2. Verificar que hay ventas en ese período
3. Ir a Historial para confirmar

### **Problema 4**: Selector de vista no persiste

**Causa**: session_state se reinicia

**Solución**:
- Normal: session_state se limpia al cerrar navegador
- Durante sesión: Debe mantenerse al cambiar de página
- Si no funciona: Bug en Streamlit, reiniciar app

---

## ✅ Resultado Final Esperado

### **Historial**:
- ✅ Visitas consolidadas (una fila por visita)
- ✅ Badges de colores para servicios/productos
- ✅ Detalles expandibles con tabla
- ✅ Totales calculados correctamente
- ✅ Exportación CSV consolidada

### **Resumen**:
- ✅ Título "Resumen" (no "Dashboard")
- ✅ Selector de vista funcional
- ✅ KPIs: Hoy, Semana, Mes
- ✅ Distribución: Gráfico + Tabla
- ✅ Top Servicios y Top Clientes (opcional)
- ✅ Cambios de configuración reflejados

### **Registro**:
- ✅ Múltiples servicios → mismo ticket_id
- ✅ Mensaje de confirmación con ticket_id
- ✅ Aparece consolidado en Historial

---

## 📊 Métricas de Éxito

| Métrica | Objetivo | Verificación |
|---------|----------|--------------|
| Visitas consolidadas | 100% | Todas las ventas del mismo ticket agrupadas |
| Totales correctos | 100% | Suma de items = total de visita |
| Migración exitosa | 100% | Todas las ventas antiguas tienen ticket_id |
| Selector funciona | 100% | Widgets aparecen/desaparecen según selección |
| Distribución visible | 100% | Gráfico + tabla con 4 categorías |
| Exportación correcta | 100% | CSV con formato consolidado |

---

**Tiempo estimado de pruebas**: 15-20 minutos  
**Prioridad**: Alta  
**Estado**: ✅ Listo para probar
