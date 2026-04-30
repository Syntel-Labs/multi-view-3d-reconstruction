// Punto de entrada del frontend. Inicializa el visor Three.js y conecta con el backend.
// Pendiente: implementar upload, llamada a /reconstruct y refresco de metricas.

import { initViewer } from './viewer/pointCloudViewer.js';

const viewerRoot = document.getElementById('viewer');
if (!viewerRoot) {
  throw new Error('Elemento #viewer no encontrado en index.html');
}

initViewer(viewerRoot);
