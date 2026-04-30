# Resumen — Proyecto Final Visión por Computadora

## Fechas clave

| Evento | Fecha |
| :--- | :--- |
| Aprobación del tema en Canvas | 23 de abril de 2026 (urgente) |
| Entrega del proyecto completo | 25-29 de mayo de 2026 |
| Presentaciones en clase | Semana 20 (25-29 mayo 2026) |

## Temas ya vistos (base disponible)

- Semana 1 — Introducción e imágenes digitales
- Semana 2 — Filtrado y convolución (Canny, Sobel, Gaussiano)
- Semana 3 — Transformadas de Fourier y morfología matemática
- Semana 4 — Características locales: SIFT, ORB, RANSAC, matching
- Semana 5 — Geometría proyectiva, modelo pinhole, homografías
- Semana 6 — Workshop: panoramas y stitching
- Semana 7 — Redes neuronales en imágenes, visión estéreo
- Semana 8 — Arquitecturas clásicas: AlexNet, VGG
- Semana 9 — Arquitecturas modernas: ResNet, Inception, MobileNet
- Semana 10 — Entrenamiento, optimización y Transfer Learning
- Semana 13 — Detección de objetos en tiempo real (YOLO, single-stage)

## Temas por ver (posibles adiciones no core)

| Semana | Tema | Potencial de incorporación |
| :--- | :--- | :--- |
| 14 | Segmentación semántica e instancia | Alto en ideas 1 y 2 |
| 15 | Transformers en Visión (ViT) | Comparativa en todas las ideas |
| 16 | Video y Tracking | Core en idea 3, extra en idea 2 |
| 17-18 | Modelos Generativos I y II (Difusión) | Marco teórico en idea 1 |

## Clasificación de ideas

| Criterio | Idea 1 — Reconstrucción 3D | Idea 2 — Control de Calidad | Idea 3 — Tracking Personas |
| :--- | :---: | :---: | :---: |
| Integración temas vistos | 5/5 | 4/5 | 3/5 |
| Métricas demostrables | 4/5 | 5/5 | 5/5 |
| Demo web viable | 4/5 | 5/5 | 3/5 |
| Temas futuros incorporables | 3/5 | 5/5 | 4/5 |
| Factibilidad en tiempo | 3/5 | 4/5 | 5/5 |
| Originalidad | 5/5 | 3/5 | 2/5 |
| Impresión en presentación | 5/5 | 4/5 | 5/5 |
| **Total** | **29/35** | **30/35** | **27/35** |

## Descripción resumida por idea

### Idea 1 — Reconstrucción 3D (Structure from Motion)

Reconstruir la geometría 3D de un objeto o escena a partir de múltiples fotografías usando SIFT, RANSAC, geometría proyectiva y triangulación. Demo web con nube de puntos interactiva en Three.js. La idea más original y técnicamente profunda, pero también la más compleja de implementar.

Archivo de detalle: [idea-1-reconstruccion-3d.md](idea-1-reconstruccion-3d.md)

### Idea 2 — Control de Calidad Visual

Detectar y clasificar defectos en productos usando Transfer Learning (ResNet/EfficientNet) y YOLO, con posibilidad de agregar segmentación a nivel de píxel. Demo web con Streamlit. La opción con mejores métricas estándar, mayor respaldo en literatura y demo web más simple de implementar.

Archivo de detalle: [idea-2-control-calidad.md](idea-2-control-calidad.md)

### Idea 3 — Tracking de Personas

Detectar y rastrear personas en video usando YOLO más un algoritmo de tracking (ByteTrack o DeepSORT). Demo en vivo con webcam durante la presentación. La opción más impactante visualmente en la presentación pero con menor integración del módulo clásico del curso.

Archivo de detalle: [idea-3-tracking-personas.md](idea-3-tracking-personas.md)

## Recomendación

- Grupo de 3 o más personas: **Idea 2** con segmentación como diferenciador. Métricas sólidas, demo web simple y temas futuros bien integrables.
- Grupo de 1 a 2 personas o preferencia por impacto visual: **Idea 1**. Más difícil, pero la más memorable y la que mejor demuestra dominio del módulo clásico.

## Pasos inmediatos

- Decidir idea definitiva entre el grupo (hoy o mañana)
- Elegir dataset y correr prueba rápida del pipeline core (30 min de código)
- Redactar descripción para Canvas: problema, enfoque y métricas esperadas
- Subir aprobación a Canvas antes del 23 de abril de 2026

## Distribución de puntos del proyecto

| Entregable | Puntos |
| :--- | :--- |
| Aprobación del tema | 3 |
| Documento | 5 |
| Repositorio | 1 |
| Video | 1 |
| Slides (máx. 10) | 5 |
| Presentación en clase | 5 |
| Calidad de solución | 5 |
| **Total** | **25** |
