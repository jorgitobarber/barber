# 📋 Guía para subir tu Barbería a GitHub y Streamlit Cloud

## 🎯 PASO 1: Crear cuenta en GitHub

1. Ve a [github.com](https://github.com)
2. Haz clic en "Sign up"
3. Crea tu cuenta con tu email
4. Verifica tu email

## 📁 PASO 2: Crear repositorio

1. Una vez en GitHub, haz clic en el botón verde "New" o "+"
2. Nombre del repositorio: `barberia-app` (o el que prefieras)
3. Descripción: "Sistema de gestión para barbería"
4. Marca como **Público** (necesario para Streamlit Cloud gratuito)
5. ✅ Marca "Add a README file"
6. Haz clic en "Create repository"

## 💻 PASO 3: Subir archivos

### Opción A: Desde la web (MÁS FÁCIL)
1. En tu repositorio, haz clic en "uploading an existing file"
2. Arrastra TODOS estos archivos desde tu carpeta:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `manifest.json`
   - `.streamlit/config.toml`
   - `.gitignore`
3. Escribe un mensaje: "Primera versión de la aplicación"
4. Haz clic en "Commit changes"

### Opción B: Con Git (si sabes usarlo)
```bash
git clone [URL_DE_TU_REPO]
cd barberia-app
# Copiar todos los archivos aquí
git add .
git commit -m "Primera versión de la aplicación"
git push
```

## ☁️ PASO 4: Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en "Sign up" y usa tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona tu repositorio `barberia-app`
5. Branch: `main`
6. Main file path: `app.py`
7. Haz clic en "Deploy!"

## ⏱️ PASO 5: Esperar despliegue

- El proceso toma 2-5 minutos
- Verás logs en pantalla
- Al final obtienes tu URL: `https://tu-usuario-barberia-app.streamlit.app`

## 📱 PASO 6: Probar en móviles

1. Abre la URL en Safari (iPhone/iPad)
2. Toca el botón "Compartir" 
3. Selecciona "Agregar a pantalla de inicio"
4. ¡Ya tienes tu app instalada!

## 🔧 PASO 7: Actualizaciones futuras

- Cada vez que cambies algo en GitHub
- Streamlit Cloud se actualiza automáticamente
- Los cambios aparecen en 1-2 minutos

## ❗ IMPORTANTE

- El repositorio DEBE ser público para la versión gratuita
- NO subas archivos .db (ya están en .gitignore)
- La primera vez puede tardar más en cargar

## 🆘 Si algo sale mal

1. Revisa que todos los archivos estén en GitHub
2. Verifica que `requirements.txt` esté correcto
3. Mira los logs en Streamlit Cloud
4. La base de datos se crea automáticamente en la nube

¡Listo! Tu barbería estará disponible 24/7 desde cualquier dispositivo 🎉
