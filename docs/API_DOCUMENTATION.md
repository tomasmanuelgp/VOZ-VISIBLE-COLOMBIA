# Documentación de API - Voz Visible

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Estado del Sistema

#### `GET /api/status`
Obtiene el estado actual del sistema y información del modelo.

**Respuesta exitosa (200):**
```json
{
  "status": "ready",
  "message": "Sistema listo",
  "model_info": {
    "num_features": 258,
    "num_classes": 30,
    "num_layers": 3
  },
  "timestamp": 1234567890.123
}
```

**Estados posibles:**
- `ready`: Sistema listo para usar
- `initializing`: Sistema inicializando
- `error`: Error en el sistema
- `missing_files`: Archivos del modelo no encontrados

---

### 2. Predicción de Lenguaje de Señas

#### `POST /api/predict`
Realiza una predicción de lenguaje de señas desde una imagen en base64.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "include_landmarks": false,
  "session_id": "optional-session-id"
}
```

**Parámetros:**
- `image` (requerido): Imagen en formato base64 con prefijo data URI
- `include_landmarks` (opcional): Si es `true`, incluye landmarks de MediaPipe en la respuesta
- `session_id` (opcional): ID de sesión para tracking

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "word": "hola",
  "confidence": 0.9875,
  "timestamp": 1234567890.123,
  "response_time_ms": 45.23,
  "audio": "data:audio/mpeg;base64,SUQzBAAAAAA...",
  "landmarks": {
    "pose": [...],
    "right_hand": [...],
    "left_hand": [...]
  }
}
```

**Errores:**
- `400`: Datos inválidos (falta imagen)
- `422`: No se pudieron extraer características
- `500`: Error interno del servidor
- `503`: Sistema no disponible

---

### 3. Subir y Analizar Imagen

#### `POST /api/upload`
Sube un archivo de imagen y la analiza.

**Request:**
- Content-Type: `multipart/form-data`
- Campo: `file` (archivo de imagen)

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "word": "hola",
  "confidence": 0.9875,
  "timestamp": 1234567890.123,
  "response_time_ms": 45.23,
  "audio": "data:audio/mpeg;base64,..."
}
```

---

### 4. Información del Modelo

#### `GET /api/model-info`
Obtiene información detallada del modelo de IA.

**Respuesta exitosa (200):**
```json
{
  "num_features": 258,
  "num_classes": 30,
  "num_layers": 3,
  "model_type": "Dense",
  "accuracy": 0.9875
}
```

---

### 5. Text-to-Speech (TTS)

#### `POST /api/tts`
Genera audio a partir de texto usando síntesis de voz.

**Request Body:**
```json
{
  "text": "Hola mundo",
  "format": "base64"
}
```

**Parámetros:**
- `text` (requerido): Texto a convertir a voz
- `format` (opcional): Formato de respuesta (`base64` o `file`, default: `base64`)

**Respuesta exitosa (200) - Formato base64:**
```json
{
  "status": "success",
  "audio": "data:audio/mpeg;base64,SUQzBAAAAAA...",
  "text": "Hola mundo",
  "timestamp": 1234567890.123
}
```

**Respuesta exitosa (200) - Formato file:**
```json
{
  "status": "success",
  "audio_url": "/api/tts/file/abc123.mp3",
  "text": "Hola mundo",
  "timestamp": 1234567890.123
}
```

#### `GET /api/tts/file/<filename>`
Descarga un archivo de audio generado previamente.

---

### 6. Logs de Traducciones

#### `GET /api/logs`
Obtiene logs de traducciones realizadas (solo para administradores).

**Query Parameters:**
- `limit` (opcional): Número máximo de registros (default: 100)
- `session_id` (opcional): Filtrar por ID de sesión
- `start_date` (opcional): Fecha de inicio en formato ISO (ej: `2024-01-01T00:00:00`)
- `end_date` (opcional): Fecha de fin en formato ISO

**Ejemplo:**
```
GET /api/logs?limit=50&session_id=abc123&start_date=2024-01-01T00:00:00
```

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "text_translated": "hola",
      "confidence": 0.9875,
      "response_time_ms": 45,
      "session_id": "abc123",
      "user_id": null
    }
  ],
  "count": 1
}
```

---

### 7. Estadísticas de Traducciones

#### `GET /api/logs/stats`
Obtiene estadísticas agregadas de las traducciones.

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "stats": {
    "total_translations": 1500,
    "avg_confidence": 0.9234,
    "avg_response_time_ms": 42.5,
    "last_translation": {
      "timestamp": "2024-01-15T10:30:00",
      "text": "hola",
      "confidence": 0.9875
    }
  }
}
```

---

### 8. Healthcheck

#### `GET /api/healthcheck`
Verifica el estado de salud del sistema.

**Respuesta exitosa (200):**
```json
{
  "status": "ok",
  "system": {
    "status": "ready",
    "message": "Sistema listo",
    "model_info": {...},
    "timestamp": 1234567890.123
  },
  "timestamp": 1234567890.123
}
```

**Estados:**
- `ok`: Sistema funcionando correctamente
- `degraded`: Sistema disponible pero con problemas

---

## WebSocket Events

### Conexión
```javascript
const socket = io();
```

### Eventos del Cliente al Servidor

#### `start_camera`
Inicia la captura de cámara.
```javascript
socket.emit('start_camera');
```

#### `stop_camera`
Detiene la captura de cámara.
```javascript
socket.emit('stop_camera');
```

#### `process_frame`
Procesa un frame de video para predicción.
```javascript
socket.emit('process_frame', {
  frame: 'data:image/jpeg;base64,...',
  include_landmarks: false,
  session_id: 'optional-session-id'
});
```

### Eventos del Servidor al Cliente

#### `prediction`
Recibe una predicción del modelo.
```javascript
socket.on('prediction', (data) => {
  console.log(data.word); // Palabra predicha
  console.log(data.confidence); // Confianza (0-1)
  console.log(data.audio); // Audio TTS (si está disponible)
  console.log(data.landmarks); // Landmarks (si se solicitaron)
});
```

#### `status`
Recibe actualizaciones de estado del sistema.
```javascript
socket.on('status', (data) => {
  console.log(data.status); // Estado del sistema
  console.log(data.message); // Mensaje descriptivo
});
```

#### `camera_status`
Recibe estado de la cámara.
```javascript
socket.on('camera_status', (data) => {
  console.log(data.status); // 'started' o 'stopped'
  console.log(data.message); // Mensaje descriptivo
});
```

---

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa
- `400 Bad Request`: Datos inválidos o faltantes
- `422 Unprocessable Entity`: No se pudieron procesar los datos
- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio no disponible

---

## Ejemplos de Uso

### Python (requests)
```python
import requests
import base64

# Leer imagen
with open('imagen.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Realizar predicción
response = requests.post('http://localhost:5000/api/predict', json={
    'image': f'data:image/jpeg;base64,{image_data}',
    'include_landmarks': False
})

result = response.json()
print(f"Palabra: {result['word']}")
print(f"Confianza: {result['confidence'] * 100}%")
```

### JavaScript (fetch)
```javascript
// Convertir imagen a base64
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const reader = new FileReader();

reader.onload = async (e) => {
  const imageData = e.target.result;
  
  const response = await fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image: imageData,
      include_landmarks: false
    })
  });
  
  const result = await response.json();
  console.log('Palabra:', result.word);
  console.log('Confianza:', result.confidence * 100 + '%');
};

reader.readAsDataURL(file);
```

### cURL
```bash
# Obtener estado
curl http://localhost:5000/api/status

# Realizar predicción
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,...",
    "include_landmarks": false
  }'

# Obtener logs
curl "http://localhost:5000/api/logs?limit=10"
```

---

## Notas Importantes

1. **Formato de Imagen**: Las imágenes deben estar en formato base64 con el prefijo `data:image/[tipo];base64,`
2. **Tamaño de Imagen**: Se recomienda imágenes de 640x480 o similar para mejor rendimiento
3. **Landmarks**: Solicitar landmarks aumenta el tiempo de procesamiento
4. **Sesiones**: El `session_id` se usa para agrupar traducciones relacionadas
5. **Logs**: Los logs se guardan automáticamente en `backend/logs/` (CSV y SQLite)
6. **TTS**: El audio se cachea para evitar regeneraciones innecesarias

---

## Limitaciones

- El modelo actual reconoce aproximadamente 30 señas
- Requiere buena iluminación y vista frontal
- El procesamiento en tiempo real tiene un delay de ~200ms entre frames
- Los landmarks solo están disponibles cuando se solicitan explícitamente

---

## Soporte

Para más información o reportar problemas:
- Email: tomasgonzalez0411@gmail.com
- GitHub: [Enlace al repositorio]

