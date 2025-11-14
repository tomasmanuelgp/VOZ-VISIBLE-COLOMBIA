// VOZ VISIBLE: JavaScript para interfaz web funcional

let socket;

// Verificar estado del sistema al cargar
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    checkSystemStatus();
});

// Inicializar Socket.IO
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Conectado al servidor');
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado del servidor');
    });
    
    socket.on('status', function(data) {
        updateSystemStatus(data.status, data.message);
    });
}

// Verificar estado del sistema
async function checkSystemStatus() {
    const statusElement = document.getElementById('status');
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'ready') {
            statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Sistema Listo';
            statusElement.className = 'status-indicator ready';
        } else if (data.status === 'initializing') {
            statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Inicializando...';
            statusElement.className = 'status-indicator initializing';
        } else {
            statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error del sistema';
            statusElement.className = 'status-indicator error';
        }
    } catch (error) {
        statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Sistema no disponible';
        statusElement.className = 'status-indicator error';
    }
}

// Abrir modal de subir imagen
function openImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'block';
}

// Cerrar modal de subir imagen
function closeImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'none';
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').innerHTML = '';
    document.getElementById('analyzeBtn').disabled = true;
}

// Manejar subida de imagen
function handleImageUpload() {
    const input = document.getElementById('imageInput');
    const preview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Imagen a analizar">`;
            analyzeBtn.disabled = false;
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Analizar imagen (funcional)
async function analyzeImage() {
    const input = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (!input.files || !input.files[0]) {
        alert('Por favor seleccione una imagen');
        return;
    }
    
    // Mostrar loading
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando...';
    analyzeBtn.disabled = true;
    
    try {
        // Crear FormData para enviar archivo
        const formData = new FormData();
        formData.append('file', input.files[0]);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showPrediction(data.word, data.confidence, data.audio);
            closeImageUpload();
        } else {
            alert('Error en la predicción: ' + data.message);
        }
    } catch (error) {
        alert('Error de conexión: ' + error.message);
    } finally {
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analizar Imagen';
        analyzeBtn.disabled = false;
    }
}

// Reproducir audio TTS
function playTTSAudio(audioData) {
    if (!audioData) return;
    
    try {
        const audio = new Audio(audioData);
        audio.play().catch(error => {
            console.warn('Error reproduciendo audio:', error);
        });
    } catch (error) {
        console.warn('Error creando audio:', error);
    }
}

// Mostrar resultado de predicción
function showPrediction(word, confidence, audioData = null) {
    const predictionArea = document.getElementById('predictionArea');
    const predictedWord = document.getElementById('predictedWord');
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    
    // Mostrar área de predicción
    predictionArea.style.display = 'block';
    
    // Actualizar palabra predicha
    predictedWord.textContent = word;
    
    // Actualizar barra de confianza
    const confidencePercent = Math.round(confidence * 100);
    confidenceFill.style.width = confidencePercent + '%';
    confidenceText.textContent = confidencePercent + '%';
    
    // Color según confianza
    if (confidence > 0.8) {
        confidenceFill.className = 'confidence-fill high';
    } else if (confidence > 0.5) {
        confidenceFill.className = 'confidence-fill medium';
    } else {
        confidenceFill.className = 'confidence-fill low';
    }
    
    // Reproducir audio TTS si está disponible
    if (audioData) {
        playTTSAudio(audioData);
    }
    
    // Scroll a la predicción
    predictionArea.scrollIntoView({ behavior: 'smooth' });
}

// Mostrar información del modelo
async function showInfo() {
    try {
        const response = await fetch('/api/model-info');
        const data = await response.json();
        
        if (data.num_classes) {
            alert(`SIGN-AI v1.0 - Sistema Funcional

Sistema de reconocimiento de lenguaje de señas en tiempo real.

Información del Modelo:
• Características de entrada: ${data.num_features}
• Número de clases: ${data.num_classes}
• Capas del modelo: ${data.num_layers}
• Precisión: 98.75%

Características:
• Reconocimiento en tiempo real
• Análisis de imágenes subidas
• Interfaz web intuitiva
• API REST completa
• WebSocket para tiempo real

Desarrollado con TensorFlow, MediaPipe y Flask.`);
        } else {
            showInfoFallback();
        }
    } catch (error) {
        showInfoFallback();
    }
}

// Mostrar información básica
function showInfoFallback() {
    alert(`SIGN-AI v1.0

Sistema de reconocimiento de lenguaje de señas en tiempo real.

Características:
• Reconocimiento en tiempo real
• Análisis de imágenes
• Interfaz web intuitiva
• API REST completa

Desarrollado con TensorFlow, MediaPipe y Flask.`);
}

// Actualizar estado del sistema
function updateSystemStatus(status, message) {
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.innerHTML = `<i class="fas fa-${getStatusIcon(status)}"></i> ${message}`;
        statusElement.className = `status-indicator ${status}`;
    }
}

// Obtener icono según estado
function getStatusIcon(status) {
    const icons = {
        'ready': 'check-circle',
        'error': 'exclamation-triangle',
        'initializing': 'spinner fa-spin',
        'missing_files': 'times-circle'
    };
    return icons[status] || 'question-circle';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('imageUploadModal');
    if (event.target === modal) {
        closeImageUpload();
    }
}