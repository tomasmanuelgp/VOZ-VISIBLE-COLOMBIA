# SIGN-AI — Instrucciones rápidas (README2)

Este archivo explica cómo ejecutar la parte web y la parte de consola/tiempo real del proyecto SIGN-AI. Está escrito en español y está pensado para ejecutarse localmente en Windows (PowerShell/Command Prompt).

---

## Resumen rápido

- La interfaz web sirve para ver la demo y usar la cámara o subir imágenes: abre http://localhost:5000 en tu navegador.
- `app.py` contiene la aplicación Flask / SocketIO y funciones de predicción: se usa para ejecutar la web o para probar endpoints (por ejemplo `/api/predict` y `/api/status`).
- `start_web.py` es un script auxiliar que verifica archivos y dependencias y arranca la app web (importa desde `app.py`).
- `main.py` es el script para ejecutar el programa de consola / tiempo real (usa la cámara, modo CLI).

---

## Requisitos previos

1. Tener Python 3.10+ (se recomienda 3.11/3.12 compatible con las versiones en `requirements_web.txt`).
2. En Windows, abrir PowerShell o Command Prompt en la carpeta del proyecto `SIGN-AI`.

---

## Nota importante sobre el ZIP descargado y el entorno virtual

Si descargaste el proyecto como un ZIP (por ejemplo desde GitHub), es normal que el archivo ZIP NO incluya el entorno virtual (`env` o `.venv`). Esto es intencional por varias razones:

- Los entornos virtuales contienen archivos específicos del sistema y binarios que ocupan mucho espacio.
- Los entornos virtuales creados en otra máquina no siempre funcionan correctamente en la tuya (diferencias de SO, rutas y versiones de Python).
- Por buenas prácticas de desarrollo, los repositorios suelen ignorar (`.gitignore`) las carpetas de entornos virtuales.

Por tanto, debes crear tu propio entorno virtual localmente. A continuación tienes pasos simples y claros (PowerShell y CMD) pensados para alguien con poca experiencia.

---

## Pasos fáciles y directos (PowerShell) — para usuarios con poca experiencia

Abre PowerShell y navega a la carpeta del proyecto `SIGN-AI` (por ejemplo `cd C:\Users\<tu_usuario>\Documents\SIGN-AI`). Luego copia y pega estos comandos uno por uno y pulsa Enter:

```powershell
# 1) Crear el entorno virtual
python -m venv env

# 2) Activar el entorno (PowerShell)
.\env\Scripts\Activate.ps1

# Si la activación falla por políticas de ejecución, puedes ejecutar este comando ANTES de activar
# (permite ejecutar scripts solo para esta sesión):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 3) Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements_web.txt

# 4) Ejecutar la aplicación web (recomendada):
python start_web.py

# Alternativa: ejecutar app.py directamente
python app.py
```

Después de ejecutar `start_web.py` o `app.py` verás mensajes en consola y, si todo va bien, la URL sugerida: http://localhost:5000. Copia esa URL en tu navegador para ver la web.

---

## Si prefieres usar el Símbolo del sistema (CMD)

Abre CMD (no PowerShell) y en la carpeta `SIGN-AI` ejecuta:

```cmd
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements_web.txt
python start_web.py
```

Esto hace exactamente lo mismo que los pasos de PowerShell pero usando la activación de CMD.

---

## Ejecutar sin "activar" el entorno virtual (método alternativo, útil si no logras activar)

Si no puedes activar el entorno por restricciones de PowerShell o por políticas, puedes llamar al intérprete Python directamente dentro del venv sin activarlo:

```powershell
# Desde PowerShell o CMD en la carpeta del proyecto:
.\env\Scripts\python.exe -m pip install --upgrade pip
.\env\Scripts\python.exe -m pip install -r requirements_web.txt
.\env\Scripts\python.exe app.py
# o para usar start_web.py
.\env\Scripts\python.exe start_web.py
```

Este método evita la activación y ejecuta el Python del entorno directamente.

---

## Qué comandos usar si solo quieres "ver la web" rápidamente

Resumen mínimo (PowerShell):

```powershell
python -m venv env
.\env\Scripts\Activate.ps1    # o usar Set-ExecutionPolicy -Scope Process ... si es necesario
pip install -r requirements_web.txt
python start_web.py
```

O, sin activar (solo pegar y ejecutar):

```powershell
.\env\Scripts\python.exe -m pip install -r requirements_web.txt
.\env\Scripts\python.exe start_web.py
```

Después de esto abre en tu navegador: http://localhost:5000

---

## Nota final y recomendaciones

- Si ves errores relacionados con paquetes que no se instalan (por ejemplo, problemas al compilar dependencias nativas), prueba a instalar las dependencias una a una o revisa el mensaje de error para ver qué falta (herramientas como `build-tools` o `Microsoft Visual C++ Build Tools` pueden ser necesarias para Windows).
- Si la web arranca pero el predictor muestra `missing_files` en `/api/status`, revisa que los archivos de `models/` y `data/processed/` existan con los nombres exactos.
- Si quieres que cree un pequeño script `examples/test_predict.py` que envíe una imagen de prueba a `/api/predict`, dímelo y lo añado.
## Crear y activar un entorno virtual (PowerShell)

En PowerShell (desde `C:\Users\<tu_usuario>\Documents\SIGN-AI`):

```powershell
python -m venv env
# Activar en PowerShell
.\env\Scripts\Activate.ps1
# Si tu PowerShell no permite ejecutar scripts, puedes usar el activate para cmd.exe:
# .\env\Scripts\activate   (usa cmd.exe o Git Bash en su lugar)
```

Si prefieres usar CMD (símbolo del sistema):

```cmd
python -m venv env
env\Scripts\activate
```

Si no puedes activar por políticas de ejecución, abre un cmd y usa la activación ahí, o ajusta la ExecutionPolicy si sabes lo que haces.

---

## Instalar dependencias

Instala las dependencias para la web (archivo incluido `requirements_web.txt`):

```powershell
pip install --upgrade pip
pip install -r requirements_web.txt
```

Nota: si quieres ejecutar solo la parte de consola/tiempo real (`main.py`) quizá también necesites las mismas dependencias (tensorflow, opencv, mediapipe, etc.).

---

## Archivos de modelo y datos (obligatorios)

La aplicación web y el programa necesitan varios archivos de datos y modelos. Los paths que busca el proyecto son (ejemplos):

- `models/Dense_Simple_patient.h5` (modelo principal)
- `models/final_correct_model.h5` (modelo alternativo)
- `data/processed/scaler_optimized.pkl`
- `data/processed/label_encoder.pkl`
- `data/processed/feature_info.json`

Si faltan archivos, `start_web.py` o `main.py` mostrará qué archivos faltan en pantalla. Asegúrate de tenerlos en esas rutas relativas dentro de la carpeta `SIGN-AI`.

---

## Ejecutar la aplicación web (modo recomendado)

1. Con el entorno virtual activado e instaladas las dependencias, ejecuta:

```powershell
python start_web.py
```

2. `start_web.py` hace una comprobación de archivos y paquetes. Si todo está OK verá mensajes y arranca el servidor.

3. Abre tu navegador y ve a:

- Página principal (interfaz): http://localhost:5000
- Página de cámara (UI que usa la cámara del navegador): http://localhost:5000/camera
- Endpoint de estado (JSON): http://localhost:5000/api/status

Si cambias el puerto en el código, ajusta la URL correspondiente.

---

## Ejecutar la aplicación web (alternativa: ejecutar `app.py` directamente)

También puedes ejecutar la app directamente (porque `start_web.py` importa y ejecuta `app.py`):

```powershell
python app.py
```

`app.py` contiene la instancia de Flask/SocketIO y la función `initialize_predictor()` que carga el modelo. Si lo ejecutas directamente verás mensajes en consola y el servidor en `http://localhost:5000`.

---

## Qué hace `app.py` exactamente

- `app.py` define la aplicación Flask y los endpoints:
  - `/` : página principal (renderiza `web/templates/index.html`).
  - `/camera` : página de cámara en tiempo real.
  - `/api/status` : devuelve estado del sistema como JSON.
  - `/api/predict` : endpoint POST para enviar una imagen (en base64 JSON) y recibir la palabra predicha y la confianza.
  - `/api/upload` : endpoint para subir ficheros (form-data `file`).
- En el arranque `initialize_predictor()` intenta cargar el modelo y los archivos asociados. Si faltan archivos marca el estado como `missing_files`.

En resumen: `app.py` es la app web; puedes usarla para probar si se detecta la seña correcta mediante la UI o llamando a los endpoints.

---

## Ver la web en el navegador (qué copiar/pegar)

Tras arrancar el servidor local (por `start_web.py` o `app.py`), copia en tu navegador exactamente:

- http://localhost:5000
- Para la cámara: http://localhost:5000/camera

Si usas otra máquina/VM o cambias `host`/`port`, ajusta `localhost`/`5000` por la dirección y puerto correctos.

---

## Probar el endpoint `/api/predict` (ejemplo rápido)

Puedes enviar una imagen en base64 (data URL) con `curl` o con una petición en Python. Ejemplo (curl):

```powershell
curl -X POST "http://localhost:5000/api/predict" -H "Content-Type: application/json" -d "{\"image\": \"data:image/jpeg;base64,<BASE64_DATA_AQUI>\"}"
```

Reemplaza `<BASE64_DATA_AQUI>` por la cadena base64 de tu imagen (sin saltos). El endpoint devuelve JSON con `word` (predicción) y `confidence`.

Ejemplo mínimo en Python (requiere `requests`):

```python
import requests
import base64

url = 'http://localhost:5000/api/predict'
with open('ejemplo.jpg','rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

payload = { 'image': f"data:image/jpeg;base64,{b64}" }
resp = requests.post(url, json=payload)
print(resp.json())
```

---

## Ejecutar el modo consola / tiempo real (cámara)

Si quieres ejecutar la versión que corre directamente en consola con la cámara (no la web):

```powershell
python main.py
```

`main.py` comprobará que existen los modelos y archivos, seleccionará el modelo disponible y arrancará un sistema de cámara (controlado desde consola). Sigue las instrucciones que muestre `main.py` en pantalla.

---

## Problemas comunes y soluciones

- "Archivos faltantes": revisa las rutas `models/` y `data/processed/` y asegúrate de que los archivos tienen exactamente esos nombres.
- Error al importar paquetes: vuelve a instalar con `pip install -r requirements_web.txt` en el entorno virtual.
- Problemas con la activación en PowerShell: usa CMD o Git Bash para activar el entorno virtual si no quieres cambiar políticas.
- Si la web arranca pero ves mensajes de "Modo Demo" en la UI, puede ser que el predictor no esté inicializado correctamente (revisa la consola para errores al cargar el modelo).
