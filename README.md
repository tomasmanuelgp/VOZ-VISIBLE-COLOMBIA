# 🤟 VOZ VISIBLE

**Sistema de Traducción de Lengua de Señas Colombiana en Tiempo Real**

Tecnología creada por estudiantes para la comunidad sorda de la jornada sabatina del Colegio José Elías Puyana.

---

## 📋 Descripción

Voz Visible es un sistema de inteligencia artificial diseñado para traducir la Lengua de Señas Colombiana (LSC) a texto y voz, buscando romper las barreras comunicativas entre personas sordas y oyentes. El proyecto utiliza MediaPipe Holistic para la extracción de puntos clave y redes neuronales CNN/RNN para la clasificación.

### 🎯 Características Principales

- ✅ **Reconocimiento en tiempo real** desde cámara web
- ✅ **Traducción a texto y voz** (Text-to-Speech)
- ✅ **Interfaz web moderna** con diseño responsive
- ✅ **Visualización de landmarks** opcional
- ✅ **Historial de predicciones**
- ✅ **Modo claro/oscuro**
- ✅ **Logging inteligente** de traducciones
- ✅ **API REST completa** con documentación
- ✅ **Precisión del 98.75%** con modelo Dense

---

## 🚀 Inicio Rápido

### Requisitos Previos

- **Python 3.10** o **3.11** (recomendado 3.10.11 o 3.10.12)
- **Cámara web** (para modo tiempo real)
- **Windows 10/11** o **Linux/Mac**
- **8GB RAM mínimo** (recomendado 16GB)

### Instalación

1. **Clonar o descargar el proyecto**
```bash
cd SIGN-AI
```

2. **Crear entorno virtual**
```powershell
# Windows PowerShell
python -m venv env
.\env\Scripts\Activate.ps1

# Si hay problemas con políticas de ejecución:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

```bash
# Linux/Mac
python -m venv env
source env/bin/activate
```

3. **Instalar dependencias**
```bash
pip install --upgrade pip
pip install -r requirements_web.txt
```

4. **Verificar archivos necesarios**
Asegúrate de tener estos archivos:
- `models/Dense_Simple_patient.h5`
- `models/final_correct_model.h5`
- `data/processed/scaler_optimized.pkl`
- `data/processed/label_encoder.pkl`
- `data/processed/feature_info.json`

5. **Ejecutar la aplicación**
```bash
python app.py
# o
python start_web.py
```

6. **Abrir en el navegador**
- Página principal: http://localhost:5000
- Cámara en tiempo real: http://localhost:5000/camera

---

## 📁 Estructura del Proyecto

```
SIGN-AI/
├── app.py                      # Aplicación Flask principal
├── config/
│   └── settings.py            # Configuración centralizada
├── src/
│   ├── inference/             # Modelo de predicción
│   ├── services/              # Servicios (predicción, TTS, logging)
│   ├── repositories/          # Acceso a datos
│   └── tts/                   # Síntesis de voz
├── web/
│   ├── templates/             # Plantillas HTML
│   └── static/                # CSS, JS, imágenes
├── models/                    # Modelos entrenados
├── data/                      # Datos procesados
├── docs/                      # Documentación
│   ├── API_DOCUMENTATION.md   # Documentación de API
│   └── architecture_decisions/
└── requirements_web.txt       # Dependencias
```

---

## 🎨 Características de la Interfaz

### Página Principal (`/`)
- **Hero Section** con diseño moderno
- **Sección "Sobre Voz Visible"** (Misión, Visión, Propósito, Equipo)
- **Sección "Aprende Más"** (Tecnología, Datos curiosos, Recursos)
- **Interfaz de traducción** mejorada con layout lado a lado
- **Footer completo** con créditos y enlaces

### Página de Cámara (`/camera`)
- **Cámara en tiempo real** con WebSocket
- **Visualización de landmarks** opcional
- **Historial de predicciones**
- **Controles de audio TTS**
- **Estadísticas en tiempo real**

---

## 🔌 API Endpoints

### Principales

- `GET /api/status` - Estado del sistema
- `POST /api/predict` - Realizar predicción desde imagen base64
- `POST /api/upload` - Subir y analizar imagen
- `POST /api/tts` - Generar audio desde texto
- `GET /api/model-info` - Información del modelo
- `GET /api/logs` - Obtener logs de traducciones
- `GET /api/logs/stats` - Estadísticas de traducciones
- `GET /api/healthcheck` - Healthcheck del sistema

### WebSocket Events

- `start_camera` - Iniciar cámara
- `stop_camera` - Detener cámara
- `process_frame` - Procesar frame de video
- `prediction` - Recibir predicción
- `status` - Actualizaciones de estado

**📖 Ver documentación completa en:** [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)

---

## 🧠 Tecnología

### Stack Tecnológico

- **Backend:**
  - Flask + SocketIO (servidor web)
  - TensorFlow 2.16.1 (modelo de IA)
  - MediaPipe Holistic (extracción de landmarks)
  - OpenCV (procesamiento de video)
  - SQLite (logs de traducciones)

- **Frontend:**
  - HTML5 + CSS3 + JavaScript
  - Socket.IO Client (tiempo real)
  - Font Awesome (iconos)

- **IA/ML:**
  - Arquitectura Dense (feed-forward)
  - 258 características de entrada
  - 30 clases de señas
  - Precisión: 98.75%

### Arquitectura del Modelo

- **MediaPipe Holistic** extrae:
  - 33 landmarks de pose (cuerpo)
  - 21 landmarks de mano derecha
  - 21 landmarks de mano izquierda
- **Preprocesamiento:** Normalización con StandardScaler
- **Modelo:** Red neuronal Dense (3 capas)
- **Salida:** 30 clases de lenguaje de señas

---

## 👥 Equipo de Desarrollo

- **Tomás González** - Programador Backend
  - Diseño de modelos IA, entrenamiento CNN/RNN
  - Manejo y limpieza de datos
  - Arquitectura del proyecto
  - Email: tomasgonzalez0411@gmail.com

- **Samuel Cardona** - Programador Backend
  - Integraciones, APIs, endpoints
  - Conexión backend-frontend

- **Andrés Ferreira** - Programador Frontend
  - UI/UX, diseño visual
  - Layout del sitio

---

## 📊 Logging y Estadísticas

El sistema registra automáticamente cada traducción con:
- Timestamp
- Texto traducido
- Confianza del modelo
- Tiempo de respuesta
- ID de sesión

Los logs se guardan en:
- `backend/logs/translations.csv` (formato CSV)
- `backend/logs/translations.db` (SQLite)

Acceso a logs:
```bash
GET /api/logs?limit=100&session_id=abc123
GET /api/logs/stats
```

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` (basado en `env.env`):

```env
# Modelos
MODEL_PRIMARY_PATH=models/Dense_Simple_patient.h5
MODEL_SECONDARY_PATH=models/final_correct_model.h5
SCALER_PATH=data/processed/scaler_optimized.pkl
LABEL_ENCODER_PATH=data/processed/label_encoder.pkl
FEATURE_INFO_PATH=data/processed/feature_info.json

# TTS
TTS_CACHE_PATH=data/cache/tts
TTS_LANGUAGE=es-co
TTS_SLOW=false

# App
APP_SECRET_KEY=tu-clave-secreta
APP_DEBUG=false
UPLOAD_FOLDER=web/uploads
```

---

## 🐛 Solución de Problemas

### Error: "Archivos faltantes"
- Verifica que existan todos los archivos en `models/` y `data/processed/`
- Revisa los nombres exactos de los archivos

### Error: "Sistema no disponible"
- Verifica que el modelo se haya cargado correctamente
- Revisa los logs en la consola

### Problemas con la cámara
- Asegúrate de dar permisos al navegador
- Verifica que la cámara no esté siendo usada por otra aplicación

### Error al instalar dependencias
- Usa Python 3.10 o 3.11
- Actualiza pip: `python -m pip install --upgrade pip`
- En Windows, puede requerir Microsoft Visual C++ Build Tools

---

## 📚 Recursos Adicionales

- **Documentación de API:** [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)
- **Decisiones Arquitectónicas:** [`docs/architecture_decisions/ADR-001-model-architecture.md`](docs/architecture_decisions/ADR-001-model-architecture.md)
- **Roadmap:** [`ROADMAP.md`](ROADMAP.md)
- **Versión de Python:** [`PYTHON_VERSION.md`](PYTHON_VERSION.md)

---

## 🎓 Propósito Social

Este proyecto nace del compromiso de apoyar directamente a estudiantes sordos del Colegio José Elías Puyana, creando una solución tecnológica que rompe barreras comunicativas y promueve la inclusión en entornos educativos.

### Misión
Facilitar la comunicación entre personas sordas y oyentes, utilizando inteligencia artificial accesible y de código abierto.

### Visión
Convertirse en una herramienta reconocida en Colombia para apoyar procesos educativos, comunicativos y sociales en comunidades sordas.

---

## 📝 Licencia

Uso educativo y sin fines de lucro.

---

## 📧 Contacto

- **Email:** tomasgonzalez0411@gmail.com
- **GitHub:** [Enlace al repositorio]

---

## 🙏 Agradecimientos

- Colegio José Elías Puyana - Jornada Sabatina
- Comunidad sorda de Colombia
- INSOR (Instituto Nacional para Sordos)

---

**Desarrollado con ❤️ por el equipo Voz Visible**
