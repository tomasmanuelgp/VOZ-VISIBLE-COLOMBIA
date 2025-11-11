
# 🤟 SIGN-AI - Sistema de Reconocimiento de Lenguaje de Señas en Tiempo Real

## 📋 Descripción del Proyecto

SIGN-AI es un sistema de reconocimiento de lenguaje de señas en tiempo real que utiliza inteligencia artificial para identificar gestos de manos y posturas corporales. El sistema está diseñado para funcionar con una cámara web y puede reconocer 30 clases diferentes de señas en español.

### 🎯 Características Principales
- **Reconocimiento en tiempo real** con cámara web
- **30 clases de lenguaje de señas** en español
- **Precisión del 98.75%** con el modelo Dense_Simple
- **Interfaz visual** con landmarks de MediaPipe
- **Soporte para múltiples modelos** entrenados

### 🧠 Tecnologías Utilizadas
- **TensorFlow 2.16.1** - Framework de machine learning
- **MediaPipe** - Detección de landmarks de manos y pose
- **OpenCV** - Procesamiento de video en tiempo real
- **scikit-learn** - Preprocesamiento de datos
- **Python 3.8+** - Lenguaje de programación

## �� Instalación y Configuración

### Prerrequisitos
- **Python 3.8 o superior**
- **Cámara web** funcional
- **Windows 10/11** (probado en Windows 10.0.26100)
- **8GB RAM mínimo** (recomendado 16GB)
- **Espacio en disco**: 2GB libres

### Paso 1: Clonar o Descargar el Proyecto
```bash
# Si tienes Git instalado
git clone [URL_DEL_REPOSITORIO]
cd SIGN-AI

# O descarga y extrae el archivo ZIP en una carpeta
```

### Paso 2: Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias desde requirements.txt
pip install -r requirements.txt
```

### Paso 4: Verificar Archivos Necesarios
Asegúrate de que existan los siguientes archivos en tu proyecto:
