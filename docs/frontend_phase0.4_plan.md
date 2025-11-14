# Fase 0.4 - Plan de mejoras Frontend

## Objetivo
Elevar la experiencia web (demo + cámara) para mostrar información más rica y alineada con la visión educativa.

## Tareas prioritarias
1. **Visualización de landmarks**
   - Integrar canvas WebGL/2D que pinte keypoints devueltos por MediaPipe
   - Mostrar superposición en cámara y en resultados de imágenes
   - Preparar endpoint opcional para enviar landmarks desde backend

2. **Historial de predicciones**
   - Mantener lista en frontend con últimas N predicciones (palabra, confianza, timestamp)
   - Permitir limpiar historial

3. **Indicadores de confianza y estado**
   - Barras/etiquetas mejoradas para confianza (colores + badges)
   - Mostrar estado del sistema (ready/error/missing files) siempre visible

4. **Feedback visual de TTS**
   - Icono animado cuando se reproduce audio
   - Botón para repetir voz de la predicción

5. **Modo claro/oscuro**
   - Toggle en UI, persistencia en `localStorage`

## Dependencias
- Requiere endpoints actuales (`/api/status`, `/api/predict`, sockets) ya funcionales
- Opcional: añadir endpoint para landmarks si se decide exponerlos desde backend

## Plan de implementación sugerido
1. Refactorizar `web/static/js/main.js` en módulos (status, upload, camera, audio)
2. Añadir componentes visuales (bar, badges, historial) en `web/templates/index.html` y `camera.html`
3. Integrar librería ligera para dibujar landmarks (p.ej. Canvas 2D + helpers)
4. Añadir estilos en `web/static/css/style.css` para modo oscuro y nuevos elementos
5. QA manual en desktop + móvil

## Entregables
- UI actualizada en `/` y `/camera`
- Documentación de uso (README)
- Capturas/GIFs opcionales para demo
