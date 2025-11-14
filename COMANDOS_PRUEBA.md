# 🚀 Comandos para Probar Voz Visible

## Paso 1: Verificar Entorno Virtual

```powershell
# Verificar si existe el entorno virtual
if (Test-Path env) { Write-Host "✓ Entorno virtual existe" } else { Write-Host "✗ Crear entorno virtual primero" }
```

Si NO existe, crear el entorno virtual:
```powershell
python -m venv env
```

## Paso 2: Activar Entorno Virtual

```powershell
# Activar entorno virtual (PowerShell)
.\env\Scripts\Activate.ps1
```

Si tienes problemas con políticas de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\env\Scripts\Activate.ps1
```

**Alternativa (CMD):**
```cmd
env\Scripts\activate
```

## Paso 3: Verificar/Instalar Dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements_web.txt
```

## Paso 4: Verificar Archivos Necesarios

```powershell
# Verificar que existan los archivos del modelo
if (Test-Path models\Dense_Simple_patient.h5) { Write-Host "✓ Modelo principal encontrado" } else { Write-Host "✗ Falta modelo principal" }
if (Test-Path data\processed\scaler_optimized.pkl) { Write-Host "✓ Scaler encontrado" } else { Write-Host "✗ Falta scaler" }
if (Test-Path data\processed\label_encoder.pkl) { Write-Host "✓ Label encoder encontrado" } else { Write-Host "✗ Falta label encoder" }
```

## Paso 5: Ejecutar la Aplicación

```powershell
# Opción 1: Usar start_web.py (recomendado)
python start_web.py

# Opción 2: Ejecutar app.py directamente
python app.py
```

## Paso 6: Probar en el Navegador

Una vez que el servidor esté corriendo, abre:

- **Página principal:** http://localhost:5000
- **Cámara en tiempo real:** http://localhost:5000/camera
- **API Status:** http://localhost:5000/api/status
- **Healthcheck:** http://localhost:5000/api/healthcheck

## Comandos de Prueba Rápida (Todo en Uno)

### Script Completo para PowerShell:

```powershell
# 1. Verificar Python
python --version

# 2. Crear entorno si no existe
if (-not (Test-Path env)) {
    Write-Host "Creando entorno virtual..."
    python -m venv env
}

# 3. Activar entorno
Write-Host "Activando entorno virtual..."
.\env\Scripts\Activate.ps1

# 4. Actualizar pip e instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements_web.txt

# 5. Verificar archivos
Write-Host "`nVerificando archivos necesarios..."
$archivos = @(
    "models\Dense_Simple_patient.h5",
    "data\processed\scaler_optimized.pkl",
    "data\processed\label_encoder.pkl",
    "data\processed\feature_info.json"
)
foreach ($archivo in $archivos) {
    if (Test-Path $archivo) {
        Write-Host "✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "✗ $archivo NO ENCONTRADO" -ForegroundColor Red
    }
}

# 6. Ejecutar aplicación
Write-Host "`nIniciando servidor..." -ForegroundColor Cyan
python app.py
```

## Probar Endpoints con cURL (PowerShell)

### Probar Status:
```powershell
curl http://localhost:5000/api/status
```

### Probar Healthcheck:
```powershell
curl http://localhost:5000/api/healthcheck
```

### Probar Logs (si hay traducciones):
```powershell
curl http://localhost:5000/api/logs?limit=10
```

### Probar Estadísticas:
```powershell
curl http://localhost:5000/api/logs/stats
```

## Probar con Python (Script de Prueba)

Crea un archivo `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Probar status
print("1. Probando /api/status...")
response = requests.get(f"{BASE_URL}/api/status")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Probar healthcheck
print("\n2. Probando /api/healthcheck...")
response = requests.get(f"{BASE_URL}/api/healthcheck")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Probar logs stats
print("\n3. Probando /api/logs/stats...")
response = requests.get(f"{BASE_URL}/api/logs/stats")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
```

Ejecutar:
```powershell
python test_api.py
```

## Solución de Problemas

### Error: "No se puede cargar el archivo"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Error: "Módulo no encontrado"
```powershell
pip install -r requirements_web.txt
```

### Error: "Archivos faltantes"
Verifica que existan:
- `models/Dense_Simple_patient.h5`
- `data/processed/scaler_optimized.pkl`
- `data/processed/label_encoder.pkl`
- `data/processed/feature_info.json`

### Error: "Puerto 5000 en uso"
Cambia el puerto en `app.py` o cierra la aplicación que usa el puerto.

## Detener el Servidor

Presiona `Ctrl + C` en la terminal donde está corriendo el servidor.

