import { initViewer } from './viewer/pointCloudViewer.js';

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('image-input');
    const metricsDiv = document.getElementById('metrics-container');

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            alert('Por favor selecciona las imagenes para subir.');
            return;
        }

        const formData = new FormData();
        for (let file of fileInput.files) {
            formData.append('images', file);
        }

        try {
            metricsDiv.innerHTML = '<p>Procesando las imagenes... Esto tomara un momento.</p>';
            
            const response = await fetch('http://localhost:8000/reconstruct', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al conectar con el backend');

            const result = await response.json();
            
            metricsDiv.innerHTML = `
                <h3>Resultados</h3>
                <p>Dataset: ${result.dataset_id}</p>
                <p>Imagenes procesadas: ${result.metrics.images_processed}</p>
                <p>Puntos generados: ${result.metrics.points_count}</p>
                <p>Error de reproyeccion: ${result.metrics.reprojection_error} px</p>
            `;

            const plyUrl = `http://localhost:8000/outputs/${result.dataset_id}/cloud.ply`;
            initViewer('viewer-container', plyUrl);

        } catch (error) {
            console.error(error);
            metricsDiv.innerHTML = '<p>Ocurrio un error al comunicarse con la API.</p>';
        }
    });

    initViewer('viewer-container', 'http://localhost:8000/outputs/controlgamecube/cloud.ply');
});
