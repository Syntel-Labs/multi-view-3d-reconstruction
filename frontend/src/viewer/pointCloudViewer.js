import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

let currentRenderer = null;
let currentAnimFrame = null;
let currentResizeHandler = null;

function cleanup() {
    if (currentAnimFrame) cancelAnimationFrame(currentAnimFrame);
    if (currentResizeHandler) window.removeEventListener('resize', currentResizeHandler);
    if (currentRenderer) currentRenderer.dispose();
    currentRenderer = null;
    currentAnimFrame = null;
    currentResizeHandler = null;
}

export function initViewer(containerId, plyUrl) {
    cleanup();

    const container = document.getElementById(containerId);

    const loaderEl = document.getElementById('viewer-loader');
    const emptyEl = document.getElementById('viewer-empty');

    const oldCanvas = container.querySelector('canvas');
    if (oldCanvas) oldCanvas.remove();

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0b0d);

    const camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.001,
        1e7
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    currentRenderer = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.6;
    controls.zoomSpeed = 1.2;
    controls.minDistance = 0.01;
    controls.maxDistance = 1e6;

    function animate() {
        currentAnimFrame = requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    const onResize = () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener('resize', onResize);
    currentResizeHandler = onResize;

    return new Promise((resolve, reject) => {
        const loader = new PLYLoader();

        loader.load(
            plyUrl,
            (geometry) => {
                geometry.computeBoundingBox();

                const pos = geometry.attributes.position.array;
                const n = pos.length / 3;

                const xs = [], ys = [], zs = [];
                for (let i = 0; i < n; i++) {
                    xs.push(pos[i * 3]);
                    ys.push(pos[i * 3 + 1]);
                    zs.push(pos[i * 3 + 2]);
                }

                const pct = (arr, p) => {
                    const s = [...arr].sort((a, b) => a - b);
                    return s[Math.floor(s.length * p)];
                };

                const [x5, x95] = [pct(xs, 0.05), pct(xs, 0.95)];
                const [y5, y95] = [pct(ys, 0.05), pct(ys, 0.95)];
                const [z5, z95] = [pct(zs, 0.05), pct(zs, 0.95)];

                const center = new THREE.Vector3(
                    (x5 + x95) / 2,
                    (y5 + y95) / 2,
                    (z5 + z95) / 2,
                );

                const span = Math.max(x95 - x5, y95 - y5, z95 - z5) || 1;

                const material = new THREE.PointsMaterial({
                    size: span * 0.008,
                    vertexColors: geometry.hasAttribute('color'),
                    color: geometry.hasAttribute('color') ? 0xffffff : 0x4fffb0,
                    sizeAttenuation: true,
                });

                const points = new THREE.Points(geometry, material);
                scene.add(points);

                scene.add(new THREE.AxesHelper(span * 0.15));

                controls.target.copy(center);
                camera.position.set(
                    center.x,
                    center.y,
                    center.z + span * 2.2
                );
                controls.update();

                if (emptyEl) emptyEl.style.display = 'none';

                resolve();
            },
            undefined,
            (error) => {
                console.error('[pointCloudViewer] Error al cargar PLY:', error);
                reject(error);
            }
        );
    });
}
