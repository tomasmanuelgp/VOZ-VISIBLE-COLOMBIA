# ADR-001: Mantener Arquitectura Dense para el Predictor

- **Fecha**: 2025-11-14
- **Estado**: Aprobado
- **Contexto**:
  - Los modelos actuales (`Dense_Simple_patient.h5`, `final_correct_model.h5`) están entrenados sobre 258 características provenientes de MediaPipe Holistic.
  - El rendimiento actual es 98.75% de precisión con inferencia rápida en CPU.
  - El dataset disponible contiene alrededor de 30 señas, insuficiente para entrenar arquitecturas temporales más complejas.

- **Decisión**:
  - Mantener temporalmente la arquitectura Dense (fully connected) como modelo principal para inferencia.
  - Posponer la migración a LSTM/Transformers hasta disponer de un dataset enriquecido y balanceado.

- **Motivaciones**:
  - Minimizar riesgo técnico y mantener compatibilidad con los archivos .h5 existentes.
  - Reducir costos de cómputo y facilitar despliegues locales/móviles.
  - Priorizar esfuerzo en refactorización, UX y TTS antes de reentrenar modelos.

- **Consecuencias**:
  - El sistema seguirá interpretando frames individuales (sin secuencias largas), lo cual limita gestos altamente temporales.
  - La documentación y configuración deben reflejar esta decisión para evitar intentos de cargar modelos secuenciales inexistentes.
  - En futuras fases, al ampliar el dataset (>100 señas) se evaluará nuevamente la migración a modelos temporales.

- **Próximos pasos**:
  1. Documentar esta decisión en README y ROADMAP (completado).
  2. Diseñar plan de expansión de dataset (Fase 3).
  3. Revaluar arquitectura una vez se disponga de datos temporales etiquetados.
