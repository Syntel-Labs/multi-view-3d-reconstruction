
import { initViewer } from './viewer/pointCloudViewer.js';

const BACKEND = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000';

const datasetSelect  = document.getElementById('dataset-select');
const uploadBtn      = document.getElementById('upload-btn');
const fileInput      = document.getElementById('image-input');
const fileDrop       = document.getElementById('file-drop');
const fileLabel      = document.getElementById('file-label');
const metricsDiv     = document.getElementById('metrics-container');
const uploadStatus   = document.getElementById('upload-status');
const statusBadge    = document.getElementById('status-badge');
const viewerLoader   = document.getElementById('viewer-loader');
const cloudInfo      = document.getElementById('cloud-info');

let activeDataset = datasetSelect.value;

function setBadge(state, text) {
    statusBadge.className = `badge badge--${state}`;
    statusBadge.textContent = text;
}

function showLoader(visible) {
    viewerLoader.style.display = visible ? 'flex' : 'none';
}

function setCloudInfo(text) {
    cloudInfo.textContent = text;
}

async function checkHealth() {
    try {
        const r = await fetch(`${BACKEND}/health`);
        if (r.ok) {
            setBadge('ok', ' backend ok');
        } else {
            setBadge('error', ' backend error');
        }
    } catch {
        setBadge('error', '✕ sin conexión');
    }
}

async function loadMetrics(dataset) {
    metricsDiv.innerHTML = `
        <div class="metrics__loading">
            <span class="spinner"></span> cargando…
        </div>`;

    try {
        const r = await fetch(`${BACKEND}/outputs/${dataset}/metrics`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const m = await r.json();
        renderMetrics(m);
    } catch (e) {
        metricsDiv.innerHTML = `<p class="metrics__error">No se encontraron métricas para <em>${dataset}</em>.<br>Ejecuta <code>make pipeline DATASET=${dataset}</code> primero.</p>`;
    }
}

function renderMetrics(m) {
    const reprErr = parseFloat(m.reprojection_error_mean ?? m.reprojection_error ?? 0);
    const inliers  = parseFloat(m.ransac_inlier_ratio ?? 0) * 100;

    const reprClass = reprErr < 1 ? '' : reprErr < 2 ? 'warn' : 'err';
    const inlierClass = inliers > 60 ? '' : inliers > 40 ? 'warn' : 'err';

    const rows = [
        { key: 'Dataset',             val: m.dataset ?? '—',                        cls: '' },
        { key: 'Imágenes',            val: m.num_images ?? '—',                     cls: '' },
        { key: 'Cámaras registradas', val: m.cameras_registered ?? m.num_images ?? '—', cls: '' },
        { key: 'Puntos 3D',           val: (m.num_3d_points ?? '—').toLocaleString?.() ?? m.num_3d_points ?? '—', cls: '' },
        { key: 'Error reproy. medio', val: reprErr ? `${reprErr.toFixed(4)} px` : '—', cls: reprClass },
        { key: 'Error reproy. med.',  val: m.reprojection_error_median != null ? `${parseFloat(m.reprojection_error_median).toFixed(4)} px` : '—', cls: reprClass },
        { key: 'Inliers RANSAC',      val: inliers ? `${inliers.toFixed(1)} %` : '—', cls: inlierClass },
    ];

    metricsDiv.innerHTML = `<div class="metrics">
        ${rows.map(r => `
            <div class="metric-row">
                <span class="metric-row__key">${r.key}</span>
                <span class="metric-row__val ${r.cls}">${r.val}</span>
            </div>`).join('')}
    </div>`;
}

async function loadDataset(dataset) {
    activeDataset = dataset;
    showLoader(true);
    setCloudInfo(`Cargando ${dataset}…`);

    const plyUrl = `${BACKEND}/outputs/${dataset}/cloud.ply`;

    // Carga métricas en paralelo con el visor
    loadMetrics(dataset);

    try {
        await initViewer('viewer-container', plyUrl);
        setCloudInfo(`${dataset} · ${plyUrl}`);
    } catch {
        setCloudInfo(`Error al cargar ${dataset}`);
    } finally {
        showLoader(false);
    }
}

async function handleUpload() {
    const files = fileInput.files;
    if (!files.length) return;

    const formData = new FormData();
    for (const file of files) formData.append('images', file);

    uploadStatus.className = 'upload-status';
    uploadStatus.textContent = 'Enviando imágenes al pipeline…';
    uploadStatus.classList.remove('hidden');
    uploadBtn.disabled = true;
    setBadge('loading', '⟳ procesando…');

    try {
        const r = await fetch(`${BACKEND}/reconstruct`, {
            method: 'POST',
            body: formData,
        });

        if (!r.ok) {
            const err = await r.json().catch(() => ({ detail: `HTTP ${r.status}` }));
            throw new Error(err.detail ?? `HTTP ${r.status}`);
        }

        const result = await r.json();
        uploadStatus.textContent = `✓ Reconstrucción completada — dataset: ${result.dataset_id}`;

        // Actualizar selector si el dataset es nuevo
        if (![...datasetSelect.options].some(o => o.value === result.dataset_id)) {
            const opt = new Option(result.dataset_id, result.dataset_id);
            datasetSelect.add(opt);
        }
        datasetSelect.value = result.dataset_id;
        await loadDataset(result.dataset_id);
        setBadge('ok', '● backend ok');

    } catch (e) {
        uploadStatus.classList.add('error');
        uploadStatus.textContent = `✕ ${e.message}`;
        setBadge('error', '✕ error');
    } finally {
        uploadBtn.disabled = false;
    }
}

fileDrop.addEventListener('dragover', e => { e.preventDefault(); fileDrop.classList.add('drag-over'); });
fileDrop.addEventListener('dragleave', () => fileDrop.classList.remove('drag-over'));
fileDrop.addEventListener('drop', e => {
    e.preventDefault();
    fileDrop.classList.remove('drag-over');
    const dt = e.dataTransfer;
    if (dt.files.length) {
        fileInput.files = dt.files;
        fileLabel.textContent = `${dt.files.length} archivo(s) seleccionado(s)`;
        uploadBtn.disabled = false;
    }
});

fileDrop.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        fileLabel.textContent = `${fileInput.files.length} archivo(s) seleccionado(s)`;
        uploadBtn.disabled = false;
    }
});

datasetSelect.addEventListener('change', () => {
    uploadStatus.classList.add('hidden');
    loadDataset(datasetSelect.value);
});

uploadBtn.addEventListener('click', handleUpload);

checkHealth();
loadDataset(activeDataset);
