import { initViewer } from './viewer/pointCloudViewer.js';

const BACKEND = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000';

const datasetSelect   = document.getElementById('dataset-select');
const loadBtn         = document.getElementById('load-btn');
const runBtn          = document.getElementById('run-btn');
const metricsDiv      = document.getElementById('metrics-container');
const pipelineStatus  = document.getElementById('pipeline-status');
const statusBadge     = document.getElementById('status-badge');
const viewerLoader    = document.getElementById('viewer-loader');
const viewerLoaderTxt = document.getElementById('viewer-loader-text');
const viewerEmpty     = document.getElementById('viewer-empty');
const cloudInfo       = document.getElementById('cloud-info');

function setBadge(state, text) {
    statusBadge.className = `badge badge--${state}`;
    statusBadge.textContent = text;
}

function showLoader(visible, text) {
    viewerLoader.style.display = visible ? 'flex' : 'none';
    if (text) viewerLoaderTxt.textContent = text;
}

function hideEmpty() {
    if (viewerEmpty) viewerEmpty.style.display = 'none';
}

function showEmpty() {
    if (viewerEmpty) viewerEmpty.style.display = 'flex';
}

function setCloudInfo(text) {
    cloudInfo.textContent = text;
}

function setPipelineStatus(text, isError) {
    pipelineStatus.classList.remove('hidden', 'error', 'success');
    if (isError) pipelineStatus.classList.add('error');
    else pipelineStatus.classList.add('success');
    pipelineStatus.textContent = text;
}

function getParams() {
    return {
        dataset:          datasetSelect.value,
        detector:         document.getElementById('p-detector').value,
        n_features:       parseInt(document.getElementById('p-nfeatures').value, 10),
        lowe_ratio:       parseFloat(document.getElementById('p-lowe').value),
        ransac_threshold: parseFloat(document.getElementById('p-ransac').value),
        min_matches:      parseInt(document.getElementById('p-minmatches').value, 10),
        window:           parseInt(document.getElementById('p-window').value, 10),
        iqr_factor:       parseFloat(document.getElementById('p-iqr').value),
        max_reproj_error: parseFloat(document.getElementById('p-maxreproj').value),
        min_parallax:     parseFloat(document.getElementById('p-parallax').value),
    };
}

async function checkHealth() {
    try {
        const r = await fetch(`${BACKEND}/health`);
        if (r.ok) {
            setBadge('ok', 'backend ok');
            return true;
        }
        setBadge('error', 'backend error');
        return false;
    } catch {
        setBadge('error', '✕ sin conexión');
        return false;
    }
}

async function loadDatasetList() {
    try {
        const r = await fetch(`${BACKEND}/datasets`);
        if (!r.ok) return;
        const data = await r.json();
        datasetSelect.innerHTML = '';
        for (const ds of data.datasets) {
            const opt = document.createElement('option');
            opt.value = ds.name;
            opt.textContent = ds.name;
            datasetSelect.appendChild(opt);
        }
    } catch {
        datasetSelect.innerHTML = '<option value="">Error cargando datasets</option>';
    }
}

function renderMetrics(m) {
    const reprErr = parseFloat(m.reprojection_error_mean ?? 0);
    const inliers = parseFloat(m.ransac_inlier_ratio ?? 0) * 100;

    const reprClass = reprErr < 1 ? '' : reprErr < 2 ? 'warn' : 'err';
    const inlierClass = inliers > 60 ? '' : inliers > 40 ? 'warn' : 'err';

    const rows = [
        { key: 'Dataset',             val: m.dataset ?? '—',                                                   cls: '' },
        { key: 'Imágenes',            val: m.num_images ?? '—',                                                 cls: '' },
        { key: 'Puntos 3D',           val: (m.num_3d_points ?? 0).toLocaleString(),                             cls: '' },
        { key: 'Error reproy. medio', val: reprErr ? `${reprErr.toFixed(4)} px` : '—',                          cls: reprClass },
        { key: 'Error reproy. med.',  val: m.reprojection_error_median != null ? `${parseFloat(m.reprojection_error_median).toFixed(4)} px` : '—', cls: reprClass },
        { key: 'Inliers RANSAC',      val: inliers ? `${inliers.toFixed(1)} %` : '—',                          cls: inlierClass },
        { key: 'Tiempo total',        val: m.time_total != null ? `${m.time_total} s` : '—',                    cls: '' },
    ];

    metricsDiv.innerHTML = `<div class="metrics">
        ${rows.map(r => `
            <div class="metric-row">
                <span class="metric-row__key">${r.key}</span>
                <span class="metric-row__val ${r.cls}">${r.val}</span>
            </div>`).join('')}
    </div>`;
}

async function loadExistingCloud(dataset) {
    if (!dataset) return;

    hideEmpty();
    showLoader(true, 'Cargando nube de puntos…');
    setCloudInfo(`Cargando ${dataset}…`);

    const plyUrl = `${BACKEND}/outputs/${dataset}/cloud.ply`;

    try {
        const r = await fetch(`${BACKEND}/outputs/${dataset}/metrics`);
        if (r.ok) {
            const m = await r.json();
            renderMetrics(m);
        } else {
            metricsDiv.innerHTML = '<p class="metrics__empty">No hay métricas disponibles. Ejecuta el pipeline primero.</p>';
        }
    } catch {
        metricsDiv.innerHTML = '<p class="metrics__empty">No hay métricas disponibles.</p>';
    }

    try {
        await initViewer('viewer-container', plyUrl);
        setCloudInfo(`${dataset} · nube cargada`);
    } catch {
        setCloudInfo(`No se encontró nube para ${dataset}`);
        showEmpty();
    } finally {
        showLoader(false);
    }
}

async function runPipeline() {
    const dataset = datasetSelect.value;
    if (!dataset) return;

    const params = getParams();

    runBtn.disabled = true;
    loadBtn.disabled = true;
    hideEmpty();
    showLoader(true, `Ejecutando pipeline sobre ${dataset}…\nEsto puede tardar varios minutos.`);
    setBadge('loading', '⟳ procesando…');
    setPipelineStatus(`Pipeline iniciado para ${dataset}…`, false);

    try {
        const r = await fetch(`${BACKEND}/reconstruct`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
        });

        if (!r.ok) {
            const err = await r.json().catch(() => ({ detail: `HTTP ${r.status}` }));
            throw new Error(err.detail ?? `HTTP ${r.status}`);
        }

        const result = await r.json();

        renderMetrics(result);
        setPipelineStatus(
            `Pipeline completado: ${result.num_3d_points} puntos 3D, ` +
            `${result.num_images} cámaras, ` +
            `reproj error = ${result.reprojection_error_mean} px`,
            false
        );

        setBadge('ok', 'backend ok');

        showLoader(true, 'Cargando nube generada…');
        const plyUrl = `${BACKEND}/outputs/${dataset}/cloud.ply`;
        try {
            await initViewer('viewer-container', plyUrl);
            setCloudInfo(`${dataset} · ${result.num_3d_points} puntos`);
        } catch {
            setCloudInfo(`Error cargando nube de ${dataset}`);
        }

    } catch (e) {
        setPipelineStatus(`Error: ${e.message}`, true);
        setBadge('error', '✕ error');
        showEmpty();
    } finally {
        showLoader(false);
        runBtn.disabled = false;
        loadBtn.disabled = false;
    }
}

loadBtn.addEventListener('click', () => {
    pipelineStatus.classList.add('hidden');
    loadExistingCloud(datasetSelect.value);
});

runBtn.addEventListener('click', runPipeline);

(async function init() {
    const ok = await checkHealth();
    if (ok) await loadDatasetList();
})();
